import asyncio
import base64
import copy
import logging
import ssl
import uuid
from abc import ABC, abstractmethod
from typing import Generator, Any, Optional, AsyncGenerator

import edge_tts
import httpx
import requests
import ujson
import websockets

from src.config import Volcengine, Minimax
from src.sdk.doubao_tts import *

logger = logging.getLogger(__name__)


# 返回base64编码的音频流
class TtsHttpClient:
    @staticmethod
    def edge_tts_stream(content: str, voice_key: str) -> Generator[str, None, None]:
        communicate = edge_tts.Communicate(content, voice_key)
        for chunk in communicate.stream_sync():
            if chunk.get('type') == 'audio':
                yield base64.b64encode(chunk.get('data')).decode()

    @classmethod
    def _get_doubao_tts_param(cls, content: str, voice_key: str) -> tuple[str, dict, dict]:
        url = 'https://openspeech.bytedance.com/api/v3/tts/unidirectional'

        headers = {
            'X-Api-App-Id': Volcengine.tts_app_id,
            'X-Api-Access-Key': Volcengine.tts_access_key,
            'X-Api-Resource-Id': 'seed-tts-1.0',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive'
        }

        payload = {
            'req_params': {
                'text': content,
                'speaker': voice_key,
                'model': 'seed-tts-1.1',
                'audio_params': {
                    'format': 'mp3'
                }
            }
        }
        return url, headers, payload

    @classmethod
    def doubao_tts_stream(cls, content: str, voice_key: str) -> Generator[str, None, None]:
        url, headers, payload = cls._get_doubao_tts_param(content, voice_key)

        resp = requests.post(url, headers=headers, json=payload, stream=True)
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            data = ujson.loads(line)
            if data.get('code') == 0 and 'data' in data and data.get('data'):
                yield data.get('data')

    @staticmethod
    async def edge_tts_stream_async(content: str, voice_key: str) -> AsyncGenerator[str, None]:
        communicate = edge_tts.Communicate(content, voice_key)
        async for chunk in communicate.stream():
            if chunk.get('type') == 'audio':
                yield base64.b64encode(chunk.get('data')).decode()

    @classmethod
    async def doubao_tts_stream_async(cls, content: str, voice_key: str) -> AsyncGenerator[str, None]:
        url, headers, payload = cls._get_doubao_tts_param(content, voice_key)
        async with httpx.AsyncClient(timeout=10) as client:
            async with client.stream('POST', url, headers=headers, json=payload) as resp:
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    data = ujson.loads(line)
                    if data.get('code') == 0 and 'data' in data and data.get('data'):
                        yield data.get('data')


class TtsCallback:
    def on_open(self) -> None:
        pass

    def on_complete(self) -> None:
        pass

    def on_error(self, error: Any) -> None:
        pass

    def on_close(self) -> None:
        pass

    def on_event(self, result: Any) -> None:
        pass


# 返回二进制音频 需要再回调函数手动处理
class TtsWebsocketClient(ABC):
    voice_key: str
    callback: TtsCallback

    def __init__(self, voice_key: str, callback: TtsCallback):
        self.voice_key = voice_key
        self.callback = callback

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def send(self, data: Any):
        pass

    @staticmethod
    def run_with_sync(func: Callable, *args):
        try:
            # 尝试获取当前运行中的循环（仅在异步上下文有效）
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # 无运行中的循环，说明在同步上下文
            loop = None

        if loop and loop.is_running():
            # 异步上下文且循环在运行：直接用 create_task 提交（同一线程）
            loop.create_task(func(*args))
        else:
            # 同步上下文或循环未运行：用 asyncio.run() 启动新循环
            asyncio.run(func(*args))


class DoubaoWsTtsClient(TtsWebsocketClient):
    ws: Optional[ClientConnection] = None
    uri = 'wss://openspeech.bytedance.com/api/v3/tts/bidirection'
    session_id: Optional[str] = None
    _receive_task: Optional[asyncio.Task] = None

    def __init__(self, voice_key: str, callback: TtsCallback):
        super().__init__(voice_key, callback)

        self.base_request: dict = {
            'req_params': {
                'speaker': self.voice_key,
                'model': 'seed-tts-1.1',
                'audio_params': {
                    'format': 'mp3'
                },
                'additions': ujson.dumps(
                    {
                        'disable_markdown_filter': True,
                        'enable_latex_tn': True
                    }
                )
            }
        }

    def open(self):
        self.run_with_sync(self.async_open)

    def close(self):
        self.run_with_sync(self.async_close)

    def send(self, data: Any):
        self.run_with_sync(self.async_send, data)

    async def async_open(self):
        # 如果已有连接 直接关闭 防止占用并发
        if self.ws:
            logger.info('DoubaoWsTtsClient连接未释放 已强制释放')
            await self.async_close()

        headers = {
            'X-Api-App-Key': Volcengine.tts_app_id,
            'X-Api-Access-Key': Volcengine.tts_access_key,
            'X-Api-Resource-Id': 'seed-tts-1.0',
            'X-Api-Connect-Id': str(uuid.uuid4())
        }

        try:
            self.ws = await websockets.connect(self.uri, additional_headers=headers, max_size=10 * 1024 * 1024)

            await start_connection(self.ws)
            await wait_for_event(self.ws, MsgType.FullServerResponse, EventType.ConnectionStarted)
            await self._start_session()

            self._receive_task = asyncio.create_task(self._receive_loop())
            self.callback.on_open()
        except Exception as e:
            logger.error(f'DoubaoWsTtsClient连接失败 {e}')
            self.callback.on_error(e)

    async def async_send(self, content: str):
        try:
            if not self.ws:
                raise Exception('DoubaoWsTtsClient未连接')

            req = copy.deepcopy(self.base_request)
            req['event'] = EventType.TaskRequest.value
            req['req_params']['text'] = content

            await task_request(self.ws, ujson.dumps(req).encode(), self.session_id)
        except Exception as e:
            logger.error(f'DoubaoWsTtsClient发送失败 {e}')
            self.callback.on_error(e)

    async def async_close(self):
        try:
            if not self.ws:
                raise Exception('DoubaoWsTtsClient未开启')

            if self._receive_task and not self._receive_task.done():
                self._receive_task.cancel()
                try:
                    await self._receive_task
                except asyncio.CancelledError:
                    pass

            await self._finish_session()
            await finish_connection(self.ws)
            await wait_for_event(self.ws, MsgType.FullServerResponse, EventType.ConnectionFinished)
            await self.ws.close()
        except Exception as e:
            logger.error(f'DoubaoWsTtsClient关闭连接失败 已强制停止 {e}')
            self.callback.on_error(e)
        finally:
            self.ws = None
            self.callback.on_close()

    async def _start_session(self):
        self.session_id = str(uuid.uuid4())
        req = copy.deepcopy(self.base_request)
        req['event'] = EventType.StartSession.value

        await start_session(self.ws, ujson.dumps(req).encode(), self.session_id)
        await wait_for_event(self.ws, MsgType.FullServerResponse, EventType.SessionStarted)

    async def _finish_session(self):
        await finish_session(self.ws, self.session_id)

    async def _receive_loop(self):
        # 阻塞等待消息，但在独立协程中不影响发送
        while self.ws:
            try:
                msg = await receive_message(self.ws)

                if msg.type == MsgType.FullServerResponse:
                    if msg.event == EventType.SessionFinished:
                        self.callback.on_complete()
                        break
                elif msg.type == MsgType.AudioOnlyServer:
                    self.callback.on_event(msg.payload)

            except Exception as e:
                logger.error(f'DoubaoWsTtsClient接收循环异常 {e}')
                self.callback.on_error(e)
                break


# 不支持流式输入
class MinimaxWsTtsClient(TtsWebsocketClient):
    ws: Optional[ClientConnection] = None
    uri = 'wss://api.minimaxi.com/ws/v1/t2a_v2'
    _receive_task: Optional[asyncio.Task] = None

    def __init__(self, voice_key: str, callback: TtsCallback):
        super().__init__(voice_key, callback)

    def open(self):
        self.run_with_sync(self.async_open)

    def close(self):
        self.run_with_sync(self.async_close)

    def send(self, data: Any):
        self.run_with_sync(self.async_send, data)

    async def async_open(self):
        # 如果已有连接 直接关闭 防止占用并发
        if self.ws:
            logger.info('MinimaxWsTtsClient连接未释放 已强制释放')
            await self.async_close()

        headers = {'Authorization': f'Bearer {Minimax.api_key}'}
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        try:
            self.ws = await websockets.connect(self.uri, additional_headers=headers, ssl=ssl_context)
            resp = ujson.loads(await self.ws.recv())
            if resp.get('event') != 'connected_success':
                raise Exception(f'MinimaxWsTtsClient连接失败 {resp}')

            await self._start_task()

            self._receive_task = asyncio.create_task(self._receive_loop())
            self.callback.on_open()
        except Exception as e:
            logger.error(f'MinimaxWsTtsClient连接失败 {e}')
            self.callback.on_error(e)

    async def async_close(self):
        try:
            if not self.ws:
                raise Exception('MinimaxWsTtsClient未开启')

            await self.ws.send(ujson.dumps({'event': 'task_finish'}))
            await self.ws.close()
        except Exception as e:
            logger.error(f'MinimaxWsTtsClient关闭连接失败 已强制关闭 {e}')
            self.callback.on_error(e)
        finally:
            self.ws = None
            self.callback.on_close()

    async def async_send(self, data: Any):
        try:
            if not self.ws:
                raise Exception('MinimaxWsTtsClient未开启')

            await self.ws.send(
                ujson.dumps(
                    {
                        'event': 'task_continue',
                        'text': data
                    }
                )
            )
        except Exception as e:
            logger.error(f'MinimaxWsTtsClient发送失败 {e}')
            self.callback.on_error(e)

    async def _start_task(self):
        start_msg = {
            'event': 'task_start',
            'model': 'speech-2.6-turbo',
            'voice_setting': {
                'voice_id': self.voice_key,
                'speed': 1,
                'vol': 1,
                'pitch': 0,
                'english_normalization': False
            },
            'audio_setting': {
                'sample_rate': 32000,
                'bitrate': 128000,
                'format': 'mp3',
                'channel': 1
            }
        }

        await self.ws.send(ujson.dumps(start_msg))
        resp = ujson.loads(await self.ws.recv())
        if resp.get('event') != 'task_started':
            raise Exception(f'MinimaxWsTtsClient创建任务失败 {resp}')

    async def _receive_loop(self):
        # 阻塞等待消息，但在独立协程中不影响发送
        while self.ws:
            try:
                resp = ujson.loads(await self.ws.recv())

                if resp.get('is_final'):
                    self.callback.on_complete()
                    break

                if 'data' in resp and 'audio' in resp["data"]:
                    audio = resp['data']['audio']
                    if not audio:
                        continue

                    audio_bytes = bytes.fromhex(audio)
                    self.callback.on_event(audio_bytes)
            except Exception as e:
                logger.error(f'MinimaxWsTtsClient接收循环异常 {e}')
                self.callback.on_error(e)
                break

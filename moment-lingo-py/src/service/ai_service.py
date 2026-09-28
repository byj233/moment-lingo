import asyncio
import base64
import logging
from enum import StrEnum
from typing import Any, AsyncGenerator, cast

import json_repair
import ujson
from dashscope.audio.asr import RecognitionCallback, RecognitionResult
from fastapi import WebSocket, WebSocketDisconnect
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate
)
from langchain_core.runnables import RunnableWithMessageHistory, RunnableLambda
from langchain_core.runnables.config import RunnableConfig
from langchain_openai import ChatOpenAI
from sqlmodel.ext.asyncio.session import AsyncSession
from sse_starlette import ServerSentEvent

from src.config import Mem0Conf
from src.db.crud import VoiceCRUD
from src.db.database import ASYNC_DATABASE_URL
from src.db.orm import Voice
from src.request.ai import OCRRequest, ExtensionTranslateRequest, AIWriteRequest
from src.utils.asr import FunAsrClient
from src.utils.common import to_lower_camel
from src.utils.llm import AIModel, LLMClient, ChatCompletion
from src.utils.lock import ConcurrentLimiter
from src.utils.meili import MeiliClient
from src.utils.mem0 import Mem0Client
from src.utils.prompt import Prompt
from src.utils.result import Result
from src.utils.sse import Sse, SseStatus
from src.utils.token import TokenManager
from src.utils.tts import TtsCallback, DoubaoWsTtsClient, MinimaxWsTtsClient

logger = logging.getLogger(__name__)


class WsMsgType(StrEnum):
    INFO = 'INFO'
    TTS = 'TTS'
    ASR = 'ASR'
    AI = 'AI'


async def _send_ws_msg(websocket: WebSocket, msg_type: WsMsgType, content: Any) -> None:
    await websocket.send_text(
        ujson.dumps({'type': msg_type.value, 'content': content}, ensure_ascii=False)
    )


async def ocr(req: OCRRequest) -> AsyncGenerator[ServerSentEvent, None]:
    model = AIModel.doubao_seed_v2_mini
    client = LLMClient(model)

    messages = [
        {'role': 'system', 'content': Prompt.ocr},
        {'role': 'user', 'content': [{'image_url': {'url': req.image_url}, 'type': 'image_url'}]}
    ]

    try:
        stream = await client.chat_completions_async(messages, stream=True)
        async for event in cast(AsyncGenerator[ServerSentEvent, None], stream):
            yield event
    except Exception as e:
        logger.error(f'文字识别失败 {e}')
        async for event in Sse.error_event_gen_async('文字识别失败', True):
            yield event


async def extension_translate(req: ExtensionTranslateRequest) -> AsyncGenerator[ServerSentEvent, None]:
    try:
        match = await MeiliClient.search_vocabulary_exact(req.content)
        if match:
            formatted = match.get('_formatted', match)
            res = {
                'word': formatted.get('word', ''),
                'translation': formatted.get('translation', ''),
                'url': f'https://www.momentlingo.cn/vocabulary/{formatted.get('vocabularyId')}'
            }

            async def _meili_stream():
                yield Sse.start_event()
                yield Sse.processing_event(res)
                yield Sse.end_event()

            async for event in _meili_stream():
                yield event
            return
    except Exception as e:
        logger.warning(f'MeiliSearch 精准匹配异常 {e}')

    model = AIModel.deepseek_v4_flash
    client = LLMClient(model)

    messages = [
        {'role': 'system', 'content': Prompt.extension_translate},
        {'role': 'user', 'content': req.content}
    ]

    try:
        stream = await client.chat_completions_async(messages, stream=True)
        async for event in cast(AsyncGenerator[ServerSentEvent, None], stream):
            yield event
    except Exception as e:
        logger.error(f'插件翻译失败 {e}')
        async for event in Sse.error_event_gen_async('翻译失败', True):
            yield event


TTS_MODEL = {
    'doubao-tts': DoubaoWsTtsClient,
    'minimax-tts': MinimaxWsTtsClient
}


async def _ai_call_checker(websocket: WebSocket, session: AsyncSession, max_available_connections: int = 10) \
    -> tuple[int, Voice] | tuple[None, None]:
    await websocket.accept()
    token = websocket.query_params.get('token')
    voice_id = int(websocket.query_params.get('voiceId', 0))

    if not token or not voice_id:
        await _send_ws_msg(websocket, WsMsgType.INFO, {'event': SseStatus.ERROR, 'text': '参数错误'})
        await websocket.close()
        return None, None

    user_id = TokenManager.validate(token)
    if user_id is None:
        logger.warning(f'无效的token {token}')
        await _send_ws_msg(websocket, WsMsgType.INFO, {'event': SseStatus.ERROR, 'text': '权限不足，无法访问'})
        await websocket.close()
        return None, None

    voice = await VoiceCRUD.one_async(session, Voice(voice_id=voice_id))
    if voice is None or voice.model is None or voice.model not in TTS_MODEL.keys():
        await websocket.close()
        return None, None

    limiter = ConcurrentLimiter(
        key='ai_call:active_connections',
        max_connections=max_available_connections,
        expire_seconds=650
    )

    current_connections, success = await limiter.acquire()

    if not success:
        logger.error(f'连接数超限 当前连接数 {current_connections}')
        await _send_ws_msg(websocket, WsMsgType.INFO, {'event': SseStatus.ERROR, 'text': '资源不足，请稍后重试'})
        await websocket.close()
        return None, None

    await _send_ws_msg(websocket, WsMsgType.INFO, {'event': SseStatus.START, 'text': '连接成功'})
    return user_id, voice


async def _ai_call_core(user_id: int, voice: Voice, enable_memory: bool, websocket: WebSocket) -> None:
    class _TtsCallBack(TtsCallback):
        def on_open(self):
            logger.info('TTS连接已打开')

        def on_close(self):
            logger.info("TTS连接已关闭")

        def on_error(self, err: Any):
            logger.error(f'TTS发生错误 {err}')

        def on_complete(self):
            logger.info('TTS生成结束')

        def on_event(self, result: Any):
            async def _task():
                nonlocal stop_event
                if stop_event.is_set():
                    return

                await _send_ws_msg(websocket, WsMsgType.TTS, base64.b64encode(result).decode())

            asyncio.run_coroutine_threadsafe(_task(), loop)

    class _AsrCallBack(RecognitionCallback):
        def on_open(self) -> None:
            logger.info('ASR连接已打开')

        def on_close(self) -> None:
            logger.info("ASR连接已关闭")

        def on_error(self, err: Any) -> None:
            logger.error(f'ASR发生错误 {err}')

        def on_event(self, result: RecognitionResult) -> None:
            try:
                if result.status_code != 200:
                    return

                async def _sentence_end() -> None:
                    nonlocal ai_task
                    if ai_task and not ai_task.done():
                        stop_event.set()
                        try:
                            await ai_task
                        except Exception as _:
                            logger.error(f'打断AI任务异常 已强制打断 {_}')
                        logger.debug('AI任务被打断')

                    user_input = result.get_sentence()["text"]
                    logger.debug('创建新的AI任务')
                    ai_task = asyncio.create_task(_ai_task(user_input))

                async def _task() -> None:
                    if result.is_sentence_end(cast(dict, result.get_sentence())):
                        logger.debug(f'ASR一句话识别结果 {result.get_sentence()["text"]}')
                        await _sentence_end()

                    await _send_ws_msg(
                        websocket,
                        WsMsgType.ASR,
                        to_lower_camel(result.get_sentence())
                    )

                asyncio.run_coroutine_threadsafe(_task(), loop)
            except Exception as _:
                logger.error(f'ASR识别失败 {_}')

    async def _get_mem0_context(query: str) -> str:
        try:
            res = await mem0_client.search(query, user_id=f'user-{user_id}')
            memories = res.get('results', []) if isinstance(res, dict) else res
            logger.debug(f'mem0检索上下文 {memories}')
            if memories:
                return 'Relevant Past Context:\n' + '\n'.join([m['memory'] for m in memories])
            return ''
        except Exception as _:
            logger.error(f'mem0检索上下文失败 {_}')
            return ''

    async def _save_mem0_memory(messages: list) -> None:
        try:
            await mem0_client.add(messages, user_id=f'user-{user_id}')
        except Exception as _:
            logger.error(f'mem0添加记忆失败 {_}')

    async def _ai_task(user_input: str) -> None:
        await tts_client.async_open()
        assistant_message = ''

        await _send_ws_msg(websocket, WsMsgType.AI, {'event': SseStatus.START})

        try:
            session_id = str(user_id)

            if enable_memory:
                context_str = await _get_mem0_context(user_input)
            else:
                context_str = ''

            # 限制保留最近 20 轮对话 (也就是 40 条 message: 20 user + 20 ai)
            temp_history = _get_session_history(session_id)
            messages = await temp_history.aget_messages()
            max_messages = 40
            if len(messages) > max_messages:
                await temp_history.aclear()
                await temp_history.aadd_messages(messages[-max_messages:])

            async for chunk in chain.astream(
                input={'input': user_input, 'context': context_str},
                config=RunnableConfig(configurable={'session_id': session_id})
            ):
                if stop_event.is_set():
                    # 提前中断
                    history = _get_session_history(session_id)
                    await history.aadd_messages([
                        HumanMessage(content=user_input),
                        AIMessage(content=assistant_message)
                    ])
                    await _send_ws_msg(websocket, WsMsgType.AI, {'event': SseStatus.END, 'msg': '打断AI任务'})

                    await asyncio.sleep(0.001)
                    if enable_memory:
                        await _save_mem0_memory([
                            {"role": 'user', 'content': user_input},
                            {"role": 'assistant', 'content': assistant_message}
                        ])
                    stop_event.clear()
                    return

                if 'response' in chunk:
                    content = chunk['response']
                elif hasattr(chunk, 'content'):
                    content = chunk.content
                else:
                    content = str(chunk)

                if content:
                    await _send_ws_msg(websocket, WsMsgType.AI, {'event': SseStatus.PROCESSING, 'text': content})

                    assistant_message += content
                    tts_client.send(content)
                    await asyncio.sleep(0.001)

            await _send_ws_msg(websocket, WsMsgType.AI, {'event': SseStatus.END})
            stop_event.clear()

            if enable_memory:
                await _save_mem0_memory([
                    {"role": 'user', 'content': user_input},
                    {"role": 'assistant', 'content': assistant_message}
                ])
        except Exception as _:
            logger.error(f'AI任务发生错误 {_}')

    def _get_session_history(session_id: str) -> SQLChatMessageHistory:
        return SQLChatMessageHistory(
            session_id,
            connection=ASYNC_DATABASE_URL,
            table_name="ai_call_history",
            async_mode=True
        )

    loop = asyncio.get_running_loop()
    model = AIModel.deepseek_v4_flash
    stop_event = asyncio.Event()

    asr_client = FunAsrClient()
    tts_client = TTS_MODEL.get(voice.model)(voice.voice_key, _TtsCallBack())
    mem0_client = Mem0Client(api_key=Mem0Conf.api_key, host=Mem0Conf.host)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(Prompt.ai_call + "\n\n{context}"),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])

    llm = ChatOpenAI(
        model=model.model,
        api_key=model.api_key,
        base_url=model.base_url,
        streaming=True,
        extra_body=model.thinking.disable
    )

    runnable = RunnableLambda(lambda x: x) | prompt | llm
    chain = RunnableWithMessageHistory(
        runnable,
        _get_session_history,
        input_messages_key="input",
        history_messages_key="history"
    )

    ai_task: asyncio.Task | None = None

    try:
        logger.info('websocket创建连接')
        asr_client.open(callback=_AsrCallBack())

        async def _receive_loop():
            while True:
                payload = await websocket.receive_bytes()
                asr_client.send(payload)

        # 维护一个计时器，超过10分钟返回失败事件
        await asyncio.wait_for(_receive_loop(), timeout=600)
    except asyncio.TimeoutError:
        logger.warning('AI通话超时，已超过10分钟限制')
        await _send_ws_msg(websocket, WsMsgType.INFO, {'event': SseStatus.ERROR, 'text': '通话超时（10分钟），已自动结束'})
        await websocket.close()
    except WebSocketDisconnect:
        logger.info('websocket断开连接')
    except Exception as e:
        logger.error(f'ai-call {e}')
    finally:
        asr_client.close()
        tts_client.close()
        limiter = ConcurrentLimiter(
            key='ai_call:active_connections',
            max_connections=0
        )
        await limiter.release()


async def ai_call(websocket: WebSocket, session: AsyncSession) -> None:
    user_id, voice = await _ai_call_checker(websocket, session)
    if user_id is None or voice is None:
        return

    enable_memory = websocket.query_params.get('memory', None) == 'open'
    await _ai_call_core(user_id, voice, enable_memory, websocket)


async def ai_write(req: AIWriteRequest) -> Result:
    model = AIModel.deepseek_v4_flash
    client = LLMClient(model)
    messages = [
        {'role': 'system', 'content': Prompt.ai_write},
        {'role': 'user', 'content': f'原文内容: {req.content}\n\n 未采用的批改内容: {req.corrections}'}
    ]

    resp = cast(ChatCompletion, await client.chat_completions_async(messages))
    res = json_repair.loads(resp.content)
    return Result.success(res)

import logging
from typing import AsyncGenerator

from sse_starlette import ServerSentEvent

from src.request.tts import TtsRequest
from src.utils.sse import Sse
from src.utils.tts import TtsHttpClient

logger = logging.getLogger(__name__)


async def edge_tts_stream(content: str, voice_key: str) -> AsyncGenerator[ServerSentEvent, None]:
    yield Sse.start_event()

    async for chunk in TtsHttpClient.edge_tts_stream_async(content, voice_key):
        yield Sse.processing_event(chunk)

    yield Sse.end_event()


async def doubao_tts_stream(content: str, voice_key: str) -> AsyncGenerator[ServerSentEvent, None]:
    yield Sse.start_event()

    async for chunk in TtsHttpClient.doubao_tts_stream_async(content, voice_key):
        yield Sse.processing_event(chunk)

    yield Sse.end_event()


async def tts(req: TtsRequest) -> AsyncGenerator[ServerSentEvent, None]:
    try:
        match req.model:
            case 'edge-tts':
                async for event in edge_tts_stream(req.content, req.voice_key):
                    yield event
            case 'doubao-tts':
                async for event in doubao_tts_stream(req.content, req.voice_key):
                    yield event
            case _:
                yield Sse.error_event('不支持的TTS模型')
    except Exception as e:
        logger.error(f'语音合成失败 {e}')
        yield Sse.error_event('语音合成失败')

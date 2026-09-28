from enum import StrEnum
from typing import Any, Generator, AsyncGenerator

import ujson
from sse_starlette import ServerSentEvent

import src.utils.common as utils


class SseStatus(StrEnum):
    START = 'START'
    END = 'END'
    PROCESSING = 'PROCESSING'
    ERROR = 'ERROR'


class Sse:
    @staticmethod
    def wrap(data: Any) -> str:
        return ujson.dumps(utils.to_lower_camel_dict({'content': data, 'timestamp': utils.timestamp()}),
            ensure_ascii=False)

    @staticmethod
    def start_event(data: Any = 'sse start') -> ServerSentEvent:
        return ServerSentEvent(event=SseStatus.START, data=Sse.wrap(data))

    @staticmethod
    def end_event(data: Any = 'sse end') -> ServerSentEvent:
        return ServerSentEvent(event=SseStatus.END, data=Sse.wrap(data))

    @staticmethod
    def processing_event(data: Any, wrap: bool = True) -> ServerSentEvent:
        return ServerSentEvent(event=SseStatus.PROCESSING, data=Sse.wrap(data) if wrap else data)

    @staticmethod
    def error_event(data: Any = 'sse error') -> ServerSentEvent:
        return ServerSentEvent(event=SseStatus.ERROR, data=Sse.wrap(data))

    @staticmethod
    def start_event_gen(data: Any | None = None) -> Generator[ServerSentEvent, None, None]:
        yield Sse.start_event(data)

    @staticmethod
    def end_event_gen(data: Any | None = None) -> Generator[ServerSentEvent, None, None]:
        yield Sse.end_event(data)

    @staticmethod
    def error_event_gen(data: Any | None = None, end: bool = False) -> Generator[ServerSentEvent, None, None]:
        yield Sse.error_event(data)
        if end:
            yield Sse.end_event()

    @staticmethod
    async def start_event_gen_async(data: Any | None = None) -> AsyncGenerator[ServerSentEvent, None]:
        yield Sse.start_event(data)

    @staticmethod
    async def end_event_gen_async(data: Any | None = None) -> AsyncGenerator[ServerSentEvent, None]:
        yield Sse.end_event(data)

    @staticmethod
    async def error_event_gen_async(data: Any | None = None, end: bool = False) -> AsyncGenerator[
        ServerSentEvent, None]:
        yield Sse.error_event(data)
        if end:
            yield Sse.end_event()

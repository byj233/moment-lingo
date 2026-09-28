import logging
import re
from contextlib import asynccontextmanager
from typing import cast, Any, Callable

import ujson
from fastapi import FastAPI, Depends, APIRouter, BackgroundTasks, WebSocket
from fastapi.exceptions import RequestValidationError, StarletteHTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sse_starlette.sse import EventSourceResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.db.database import get_async_session
from src.request.ai import OCRRequest, ExtensionTranslateRequest, AIWriteRequest
from src.request.essay import EssayCorrectRequest
from src.request.sms import SmsRequest
from src.request.tts import TtsRequest
from src.service import ai_service, sms_service, tts_service, essay_service
from src.utils.lock import ConcurrentLimiter
from src.utils.result import Result

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info('服务启动中...')
    await essay_service.failed_tasks()
    yield
    logger.info('服务关闭中...')
    # 释放所有的并发锁
    limiter = ConcurrentLimiter(key='ai_call:active_connections', max_connections=0)
    await limiter.clear()
    logger.info('并发锁释放完成')


app = FastAPI(lifespan=lifespan)
ai_router = APIRouter(prefix='/ai')
essay_router = APIRouter(prefix='/essay')

app.add_middleware(
    cast(Any, CORSMiddleware),
    allow_origins=['http://localhost:5173', 'https://www.momentlingo.cn'],
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'OPTIONS'],
    allow_headers=['*']
)


# 中间件：将请求体中的驼峰命名转换为下划线命名
@app.middleware('http')
async def camel_case_middleware(request: Request, call_next: Callable) -> JSONResponse | None:
    if request.method in ['GET', 'POST', 'PUT', 'PATCH']:
        content_type = request.headers.get('content-type')
        if content_type and "application/json" in content_type:
            try:
                body = await request.json()
                snake_body = {}
                for key, value in body.items():
                    snake_key = re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower()
                    snake_body[snake_key] = value
                request._body = ujson.dumps(snake_body).encode()
            except Exception as e:
                logger.error(f'请求体JSON格式错误 {e}')
                return JSONResponse(content={'error': '请求体JSON格式错误'}, status_code=400)

    return await call_next(request)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, e: RequestValidationError) -> JSONResponse:
    return JSONResponse(content=Result.error(f'参数校验异常 {e}', code=422).model_dump())


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_: Request, e: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(content=Result.error(f'HTTP异常 {e}', code=404).model_dump())


@app.exception_handler(Exception)
async def http_exception_handler(_: Request, e: Exception) -> JSONResponse:
    logger.error(f'服务器内部错误 {e}')
    return JSONResponse(content=Result.error('服务器内部错误').model_dump())


@app.post('/tts')
async def tts(req: TtsRequest) -> EventSourceResponse:
    return EventSourceResponse(tts_service.tts(req))


@app.post('/sms')
async def sms(req: SmsRequest) -> Result:
    return await sms_service.send_msg(req)


@ai_router.post('/extension/translate')
async def extension_translate(req: ExtensionTranslateRequest) -> EventSourceResponse:
    return EventSourceResponse(ai_service.extension_translate(req))


@ai_router.post('/ocr')
async def ocr(req: OCRRequest) -> EventSourceResponse:
    return EventSourceResponse(ai_service.ocr(req))


@essay_router.post('/correct/task')
async def put_correct_essay_task(
    req: EssayCorrectRequest,
    background_tasks: BackgroundTasks
) -> Result:
    return await essay_service.put_essay_correct_task(req, background_tasks)


@app.websocket('/ai/call')
async def ws_ai_call(websocket: WebSocket, session: AsyncSession = Depends(get_async_session)) -> None:
    await ai_service.ai_call(websocket, session)


@app.post('/ai/write')
async def ai_write(req: AIWriteRequest) -> Result:
    return await ai_service.ai_write(req)


def register_routers():
    app.include_router(ai_router)
    app.include_router(essay_router)

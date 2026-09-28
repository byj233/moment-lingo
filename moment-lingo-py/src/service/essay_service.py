import logging
import uuid
from enum import StrEnum
from typing import cast

import json_repair
from fastapi import BackgroundTasks

from src.db import orm
from src.db.crud import EssayCRUD
from src.db.database import get_async_redis_client, get_async_db
from src.request.essay import EssayCorrectRequest
from src.utils.common import beijing_time
from src.utils.llm import AIModel, LLMClient, ChatCompletion
from src.utils.prompt import Prompt
from src.utils.result import Result

logger = logging.getLogger(__name__)


class TaskStatus(StrEnum):
    PENDING = 'PENDING'
    SUCCEED = 'SUCCEED'
    FAILED = 'FAILED'


async def failed_tasks() -> None:
    r = await get_async_redis_client()
    keys = await r.keys('essay:correct:*')
    for key in keys:
        status = await r.hget(key, 'status')
        if status == TaskStatus.PENDING:
            await r.hset(
                key,
                mapping={
                    'status': TaskStatus.FAILED,
                    'error': '服务重启导致任务失败',
                    'updatedAt': beijing_time()
                }
            )
            await r.persist(key)
            logger.info(f'作文批改任务 {key} 因服务重启导致任务失败')


async def put_essay_correct_task(req: EssayCorrectRequest, background_tasks: BackgroundTasks) -> Result:
    task_id = str(uuid.uuid4())
    key = f'essay:correct:{req.user_id}:{task_id}'
    now = beijing_time()
    r = await get_async_redis_client()

    await r.hset(
        key,
        mapping={
            'taskId': task_id,
            'status': TaskStatus.PENDING,
            'content': req.content,
            'createdAt': now,
            'updatedAt': now
        }
    )
    await r.expire(key, 60 * 60 * 2)

    async def _task():
        nonlocal now
        _r = await get_async_redis_client()

        try:
            model = AIModel.deepseek_v4_flash
            client = LLMClient(model)
            messages = [
                {'role': 'system', 'content': Prompt.correct_essay},
                {'role': 'user', 'content': req.content}
            ]

            resp = cast(ChatCompletion, await client.chat_completions_async(messages, thinking=True))
            res = json_repair.repair_json(resp.content, ensure_ascii=False)

            async with get_async_db() as _session:
                await EssayCRUD.add_async(
                    _session,
                    orm.Essay(
                        user_id=req.user_id,
                        content=req.content,
                        result=res,
                        created_at=now,
                        type=1
                    )
                )

            await _r.hset(key, mapping={'status': TaskStatus.SUCCEED, 'updatedAt': beijing_time()})
        except Exception as e:
            logger.error(f'put-correct-essay-task {e}')
            await _r.hset(key, mapping={'status': TaskStatus.FAILED, 'error': str(e), 'updatedAt': beijing_time()})
            await _r.persist(key)

    background_tasks.add_task(_task)
    return Result.success()

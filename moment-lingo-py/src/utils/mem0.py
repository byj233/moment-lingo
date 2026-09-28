import logging

import httpx

logger = logging.getLogger(__name__)


class Mem0Client:
    def __init__(self, api_key: str, host: str) -> None:
        self.api_key = api_key
        # 去除可能存在的尾部斜杠，保证拼接 URL 时的一致性
        self.host = host.rstrip('/')

    def _get_header(self) -> dict:
        return {'Authorization': f'Token {self.api_key}'}

    async def add(self, messages: list, user_id: str, async_mode: bool = True) -> list | dict:
        url = f'{self.host}/v1/memories'
        payload = {
            'messages': messages,
            'user_id': user_id,
            "async_mode": async_mode
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, headers=self._get_header(), json=payload, timeout=10.0)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                logger.error(f'mem0添加记忆失败 {e}')
                raise e

    async def search(self, query: str, user_id: str) -> list | dict:
        url = f'{self.host}/v2/memories/search'
        payload = {
            'query': query,
            'filters': {
                'user_id': user_id
            }
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, headers=self._get_header(), json=payload, timeout=10.0)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                logger.error(f'mem0搜索记忆失败 {e}')
                raise e

    async def delete_all(self, user_id: str):
        url = f'{self.host}/v1/memories?user_id={user_id}'

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.delete(url, headers=self._get_header(), timeout=10.0)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                logger.error(f'mem0删除记忆失败 {e}')
                raise e

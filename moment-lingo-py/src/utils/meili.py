import asyncio
import logging
from typing import Any

import meilisearch

from src.config import MeiliConf

logger = logging.getLogger(__name__)


class MeiliClient:
    client = meilisearch.Client(MeiliConf.host, MeiliConf.api_key)
    index_name = 'vocabulary'

    @classmethod
    async def search_vocabulary_exact(cls, query: str) -> dict[str, Any] | None:
        """
        精准查询单词
        """
        def _search():
            try:
                # 转义单引号以防止查询语法错误
                safe_query = query.replace("'", "\\'")

                index = cls.client.index(cls.index_name)
                res = index.search(query, {
                    'attributesToSearchOn': ['word', 'translation'],
                    'filter': f"word = '{safe_query}'"
                })

                hits = res.get('hits', [])
                if hits:
                    return hits[0]
                return None
            except Exception as e:
                logger.error(f'MeiliSearch查询失败 {e}')
                return None

        return await asyncio.to_thread(_search)

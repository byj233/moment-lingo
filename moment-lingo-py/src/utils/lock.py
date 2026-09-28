import logging
from src.db.database import get_async_redis_client

logger = logging.getLogger(__name__)

class ConcurrentLimiter:
    """基于 Redis 的并发限制器"""
    
    def __init__(self, key: str, max_connections: int, expire_seconds: int = 3600):
        self.key = key
        self.max_connections = max_connections
        self.expire_seconds = expire_seconds

        # 尝试获取锁：原子递增，如果超限则递减回滚
        self._acquire_script = """
        local current = redis.call('INCR', KEYS[1])
        if current > tonumber(ARGV[1]) then
            redis.call('DECR', KEYS[1])
            return {tostring(current - 1), 0}
        end
        redis.call('EXPIRE', KEYS[1], tonumber(ARGV[2]))
        return {tostring(current), 1}
        """

        # 释放锁：如果有值且大于0，则递减
        self._release_script = """
        local current = redis.call('GET', KEYS[1])
        if current and tonumber(current) > 0 then
            redis.call('DECR', KEYS[1])
            return 1
        end
        return 0
        """

    async def acquire(self) -> tuple[int, bool]:
        """
        尝试获取并发名额
        :return: (当前连接数, 是否成功获取)
        """
        redis = await get_async_redis_client()
        try:
            result = await redis.eval(
                self._acquire_script,
                1,
                self.key,
                self.max_connections,
                self.expire_seconds
            )
            return int(result[0]), bool(result[1])
        except Exception as e:
            logger.error(f'ConcurrentLimiter acquire 异常: {e}')
            return 0, False

    async def clear(self) -> bool:
        """
        清空并发限制记录
        """
        redis = await get_async_redis_client()
        try:
            await redis.delete(self.key)
            return True
        except Exception as e:
            logger.error(f'ConcurrentLimiter clear 异常: {e}')
            return False

    async def release(self) -> bool:
        """
        释放并发名额
        :return: 是否成功释放
        """
        redis = await get_async_redis_client()
        try:
            result = await redis.eval(
                self._release_script,
                1,
                self.key
            )
            return bool(result)
        except Exception as e:
            logger.error(f'ConcurrentLimiter release 异常: {e}')
            return False

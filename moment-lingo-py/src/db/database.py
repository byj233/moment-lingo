from contextlib import contextmanager, asynccontextmanager
from typing import Generator, AsyncGenerator
from urllib.parse import quote_plus

import redis
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import create_engine, Session
from sqlmodel.ext.asyncio.session import AsyncSession

from src.config import DBConf, RedisConf

encoded_password = quote_plus(DBConf.password)

DATABASE_URL = f'mysql+pymysql://{DBConf.username}:{encoded_password}@{DBConf.host}:{DBConf.port}/{DBConf.db}'
ASYNC_DATABASE_URL = f'mysql+aiomysql://{DBConf.username}:{encoded_password}@{DBConf.host}:{DBConf.port}/{DBConf.db}'

DB_CONFIG = {
    'pool_size': 10,  # 连接池默认保持的连接数
    'max_overflow': 20,  # 超过pool_size时允许的临时连接数
    'pool_recycle': 3600,  # 1小时(3600秒)回收一次连接，需小于MySQL的wait_timeout
    'pool_pre_ping': True,  # 获取连接前先ping通测试，确保连接有效
    'pool_timeout': 30,  # 获取连接的超时时间
    'echo': True  # 生产环境关闭SQL日志
}

engine = create_engine(
    DATABASE_URL,
    **DB_CONFIG
)

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    **DB_CONFIG
)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as conn:
        yield conn


@contextmanager
def get_db() -> Generator[Session, None, None]:
    session = Session(engine)
    try:
        yield session
        session.commit()  # 成功时提交
    except Exception as e:
        session.rollback()  # 异常时回滚
        raise e
    finally:
        session.close()  # 确保关闭


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(async_engine) as session:
        yield session


@asynccontextmanager
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    session = AsyncSession(async_engine)
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()

REDISC_CONFIG = {
    'host': RedisConf.host,
    'port': RedisConf.port,
    'password': RedisConf.password,
    'db': RedisConf.db,
    'decode_responses': True,
    'max_connections': 20,
    'socket_connect_timeout': 20
}
pool = redis.ConnectionPool(**REDISC_CONFIG)
async_pool = redis.asyncio.ConnectionPool(**REDISC_CONFIG)


def get_redis_client() -> redis.Redis:
    return redis.Redis(connection_pool=pool)


async def get_async_redis_client() -> redis.asyncio.Redis:
    return redis.asyncio.Redis(connection_pool=async_pool)

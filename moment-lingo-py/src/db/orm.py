from datetime import datetime

from snowflake import SnowflakeGenerator
from sqlmodel import Column, Field, DATETIME, SQLModel

from src.utils.common import beijing_time

sf = SnowflakeGenerator(1)


def get_snowflake_id() -> int:
    return next(sf)


class Essay(SQLModel, table=True):
    __tablename__ = 'essay'

    essay_id: int = Field(primary_key=True, default_factory=get_snowflake_id)
    user_id: int
    content: str
    result: str
    type: int
    created_at: datetime = Field(sa_column=Column(DATETIME, nullable=False, default=beijing_time))
    updated_at: datetime = Field(
        sa_column=Column(DATETIME, nullable=False, default=beijing_time, onupdate=beijing_time))


class Voice(SQLModel, table=True):
    __tablename__ = 'voice'

    voice_id: int = Field(primary_key=True, default_factory=get_snowflake_id)
    voice_name: str
    voice_key: str
    type: str
    model: str
    tags: str
    weight: int
    created_at: datetime = Field(sa_column=Column(DATETIME, nullable=False, default=beijing_time))
    updated_at: datetime = Field(
        sa_column=Column(DATETIME, nullable=False, default=beijing_time, onupdate=beijing_time))

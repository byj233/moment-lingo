from typing import cast

from src.db.database import get_redis_client


class TokenManager:
    @staticmethod
    def validate(token: str) -> int | None:
        r = get_redis_client()
        return cast(int, r.get(f'token:{token}'))

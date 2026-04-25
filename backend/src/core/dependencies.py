from typing import Annotated, cast

from fastapi import Depends
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src.postgres.session import get_session

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_redis(request: Request) -> Redis:
    return cast(Redis, request.app.state.redis)


RedisDep = Annotated[Redis, Depends(get_redis)]

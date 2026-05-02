from typing import Annotated, cast

from fastapi import (
    Depends,
    Cookie,
    HTTPException,
    status,
)
from fastapi.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src.core.postgres import get_session
from src.user.repository import UserRepository

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_redis(request: Request) -> Redis:
    return cast(Redis, request.app.state.redis)


def get_access_token(
    access_token: str = Cookie(default=None, include_in_schema=False)
) -> str:
    """get access token"""
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have not provided an access token",
        )
    return access_token


def get_refresh_token(
    refresh_token: str = Cookie(default=None, include_in_schema=False)
) -> str:
    """get refresh token"""
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have not provided a refresh token",
        )
    return refresh_token


def get_user_repository(session: SessionDep) -> UserRepository:
    """get user repository"""
    return UserRepository(session)


RedisDep = Annotated[Redis, Depends(get_redis)]
AccessTokenDep = Annotated[str, Depends(get_access_token)]
RefreshTokenDep = Annotated[str, Depends(get_refresh_token)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]

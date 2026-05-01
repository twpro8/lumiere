from datetime import datetime, timezone
from uuid import UUID
from typing import Annotated

from fastapi import HTTPException, Depends, status

from src.core.dependencies import SessionDep
from src.core.dependencies import AccessTokenDep, UserRepositoryDep
from src.auth.security import decode_token
from src.user.repository import UserRepository
from src.user.schemas import UserSchema
from src.user.service import UserService


def get_current_user_id(access_token: AccessTokenDep) -> UUID:
    """get current user id from access token"""
    payload = decode_token(access_token)
    if not payload.sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token!",
        )
    if payload.expire < datetime.now(timezone.utc):
        raise HTTPException(401, "Token expired")
    return payload.sub


async def get_current_user(
    user_id: UserIdDep,
    user_service: UserServiceDep,
) -> UserSchema:
    """get current user"""
    return await user_service.get_user(user_id)


def get_user_service(
    session: SessionDep,
    user_repository: UserRepositoryDep,
) -> UserService:
    """get user service"""
    return UserService(session, user_repository)


def get_user_repository(session: SessionDep) -> UserRepository:
    """get user repository"""
    return UserRepository(session)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
UserIdDep = Annotated[UUID, Depends(get_current_user_id)]
CurrentUserDep = Annotated[UserSchema, Depends(get_current_user)]

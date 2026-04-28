from uuid import UUID
from typing import Annotated

from fastapi import HTTPException, Depends, Cookie, status

from src.core.dependencies import SessionDep
from src.auth.security import decode_token
from src.user.repository import UserRepository
from src.user.schemas import UserSchema
from src.user.service import UserService


def get_token(access_token: str = Cookie(default=None)) -> str:
    """get access token"""
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have not provided an access token!",
        )
    return access_token


def get_current_user_id(access_token: AccessTokenDep) -> UUID:
    """get current user id from access token"""
    user_id = decode_token(access_token).sub
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token!",
        )
    return user_id


async def get_current_user(
    user_id: UserIdDep,
    user_service: UserServiceDep,
) -> UserSchema:
    """get current user"""
    return await user_service.get_current_user(user_id)


async def get_user_service(
    session: SessionDep,
    user_repository: UserRepositoryDep,
) -> UserService:
    """get user service"""
    return UserService(session, user_repository)


async def get_user_repository(session: SessionDep) -> UserRepository:
    """get user repository"""
    return UserRepository(session)


AccessTokenDep = Annotated[str, Depends(get_token)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
UserIdDep = Annotated[UUID, Depends(get_current_user_id)]
CurrentUserDep = Annotated[UserSchema, Depends(get_current_user)]

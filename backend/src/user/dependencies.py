from uuid import UUID
from typing import Annotated

from fastapi import Request, HTTPException, Depends

from src.core.dependencies import SessionDep
from src.auth.security import decode_token
from src.user.service import UserService


def get_token(request: Request) -> str:
    """get access token"""
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=401, detail="You have not provided an access token!"
        )
    return access_token


def get_current_user_id(access_token: str = Depends(get_token)) -> UUID:
    """get current user id from access token"""
    user_id = decode_token(access_token).sub
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token!")
    return user_id


async def get_user_service(session: SessionDep) -> UserService:
    """get user service"""
    return UserService(session)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]

UserIdDep = Annotated[UUID, Depends(get_current_user_id)]

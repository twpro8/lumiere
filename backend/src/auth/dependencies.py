from typing import Annotated

from fastapi import HTTPException, Cookie, status, Depends

from src.auth.service import AuthService
from src.core.dependencies import SessionDep
from src.user.repository import UserRepository


def get_access_token(
    access_token: str = Cookie(default=None, include_in_schema=False)
) -> str:
    """get access token"""
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You have not provided an access token!",
        )
    return access_token


def get_auth_service(
    session: SessionDep,
    user_repository: UserRepositoryDep,
) -> AuthService:
    """get auth service"""
    return AuthService(session, user_repository)


def get_user_repository(session: SessionDep) -> UserRepository:
    """get user repository"""
    return UserRepository(session)


AccessTokenDep = Annotated[str, Depends(get_access_token)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]

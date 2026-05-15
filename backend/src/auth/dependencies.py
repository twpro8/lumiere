from typing import Annotated

from fastapi import Depends

from src.auth.repository import AuthRepository
from src.auth.service import AuthService
from src.core.dependencies import SessionDep, RedisDep
from src.user.dependencies import UserRepositoryDep


def get_auth_service(
    session: SessionDep,
    user_repository: UserRepositoryDep,
    auth_repository: AuthRepositoryDep,
    client_redis: RedisDep,
) -> AuthService:
    """get auth service"""
    return AuthService(
        session,
        user_repository,
        auth_repository,
        client_redis,
    )


def get_auth_repository(session: SessionDep) -> AuthRepository:
    """get auth repository"""
    return AuthRepository(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
AuthRepositoryDep = Annotated[AuthRepository, Depends(get_auth_repository)]

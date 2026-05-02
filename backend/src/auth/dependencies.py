from typing import Annotated

from fastapi import Depends

from src.auth.service import AuthService
from src.core.dependencies import SessionDep, UserRepositoryDep, RedisDep


def get_auth_service(
    session: SessionDep,
    user_repository: UserRepositoryDep,
    client_redis: RedisDep,
) -> AuthService:
    """get auth service"""
    return AuthService(session, user_repository, client_redis)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

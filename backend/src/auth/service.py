from datetime import datetime, timezone, timedelta
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src.core.config import settings
from src.user.repository import UserRepository
from src.auth.repository import AuthRepository
from src.core.services import BaseService
from src.auth.schemas import (
    UserCreateSchema,
    TokenPair,
    RefreshTokenCreateSchema,
)
from src.auth.security import (
    hash_password,
    hash_token,
    create_access_token,
    verify_password,
    create_refresh_token,
)
from src.auth.schemas import (
    AccessTokenPayload,
    UserRegisterSchema,
    UserLoginSchema,
)


class AuthService(BaseService):

    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        auth_repository: AuthRepository,
        client_redis: Redis,
    ) -> None:
        super().__init__(session)
        self.user_repository = user_repository
        self.auth_repository = auth_repository
        self.client_redis = client_redis

    async def create_user(self, user_data: UserRegisterSchema) -> None:
        """
        Create a new user
        :param user_data: - user data
        """
        try:
            user_data_to_add = UserCreateSchema(
                **user_data.model_dump(),
                password_hash=hash_password(user_data.password),
            )
            await self.user_repository.create(user_data_to_add)
            await self.session.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User already exists"
            )

    async def authenticate_user(self, user_data: UserLoginSchema) -> TokenPair:
        """
        Authenticate a user
        :param user_data: - user data
        """
        user = await self.user_repository.get_one(username=user_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if not verify_password(user_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password",
            )

        return await self._issue_tokens(user.id)

    async def refresh(self, refresh_token_raw: str) -> TokenPair:
        """
        Refresh token
        """
        token_hash = hash_token(refresh_token_raw)
        refresh_token = await self.auth_repository.get_one(
            token_hash=token_hash,
        )
        if not refresh_token or refresh_token.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")

        if refresh_token.is_revoked:
            await self.auth_repository.revoke_all_tokens(refresh_token.user_id)
            await self.session.commit()
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Compromise detected")

        user_id = refresh_token.user_id
        if not user_id:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")

        await self.auth_repository.revoke_token(refresh_token.id)
        await self.session.commit()

        return await self._issue_tokens(user_id)

    async def _issue_tokens(self, user_id: UUID) -> TokenPair:
        """
        Issue tokens
        :param user_id: - user id
        :return: - tokens
        """
        payload = AccessTokenPayload(sub=user_id)
        access_token = create_access_token(payload)
        refresh_token, refresh_token_hash = create_refresh_token()

        refresh_token_to_add = RefreshTokenCreateSchema(
            token_hash=refresh_token_hash,
            user_id=user_id,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        await self.auth_repository.create(refresh_token_to_add)
        await self.session.commit()

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
        )

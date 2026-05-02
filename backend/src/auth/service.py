from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from src.core.config import settings
from src.user.repository import UserRepository
from src.core.services import BaseService
from src.auth.schemas import UserCreateSchema, TokenPair
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
        client_redis: Redis,
    ) -> None:
        super().__init__(session)
        self.user_repository = user_repository
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

    async def refresh(self, refresh_token: str) -> TokenPair:
        """
        Refresh token
        """
        token_hash = hash_token(refresh_token)
        redis_key = f"refresh_token:{token_hash}"

        user_id = await self.client_redis.getdel(redis_key)

        if not user_id:
            raise HTTPException(401, "Invalid refresh token")

        return await self._issue_tokens(UUID(user_id))

    async def _issue_tokens(self, user_id: UUID) -> TokenPair:
        """
        Issue tokens
        :param user_id: - user id
        :return: - tokens
        """
        payload = AccessTokenPayload(sub=user_id)
        access_token = create_access_token(payload)
        refresh_token, refresh_token_hash = create_refresh_token()

        redis_key = f"refresh_token:{refresh_token_hash}"
        await self.client_redis.setex(
            redis_key,
            settings.REFRESH_TOKEN_EXPIRE_SECONDS,
            str(payload.sub),
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
        )

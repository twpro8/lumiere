from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.repository import UserRepository
from src.core.services import BaseService
from src.auth.schemas import (
    UserCreateSchema,
)
from src.auth.security import (
    hash_password,
    create_access_token,
    verify_password,
)
from src.auth.schemas import (
    AccessTokenPayload,
    UserRegisterSchema,
    UserLoginSchema,
)


class AuthService(BaseService):

    def __init__(self, session: AsyncSession, user_repository: UserRepository):
        super().__init__(session)
        self.user_repository = user_repository

    async def create_user(self, user_data: UserRegisterSchema) -> None:
        """
        Create a new user
        :param user_data: - user data
        """
        try:
            user_data_to_add = UserCreateSchema(
                **user_data.model_dump(),
                password_hash=hash_password(user_data.password)
            )
            await self.user_repository.create(user_data_to_add)
            await self.session.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User already exists!"
            )

    async def authenticate_user(self, user_data: UserLoginSchema) -> str:
        """
        Authenticate a user
        :param user_data: - user data
        """
        user = await self.user_repository.get_one(username=user_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found!",
            )

        if not verify_password(user_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password!",
            )
        payload = AccessTokenPayload(sub=user.id)
        return create_access_token(payload)

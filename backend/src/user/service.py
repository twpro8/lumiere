from uuid import UUID

from fastapi import HTTPException, Response
from sqlalchemy.exc import IntegrityError

from src.auth.schemas import AccessTokenPayload
from src.core.services import BaseService
from src.user.schemas import (
    UserCreateRequestSchema,
    UserCreateSchema,
    UserLoginSchema,
    UserSchema,
)
from src.auth.security import (
    hash_password,
    create_access_token,
    verify_password,
)
from src.user.repository import UserRepository


class UserService(BaseService):

    async def create_user(self, user_data: UserCreateRequestSchema) -> None:
        """
        Create a new user
        :param user_data: - user data
        """
        try:
            user_data_to_add = UserCreateSchema(
                **user_data.model_dump(),
                password_hash=hash_password(user_data.password)
            )
            await UserRepository(self.session).create(user_data_to_add)
            await self.session.commit()
        except IntegrityError:
            raise HTTPException(status_code=409, detail="User already exists!")

    async def authenticate_user(
        self, user_data: UserLoginSchema, response: Response
    ) -> None:
        """
        Authenticate a user
        :param user_data: - user data
        :param response: - user data
        """
        user = await UserRepository(self.session).get_one(username=user_data.username)
        if not user:
            raise HTTPException(
                status_code=401, detail="Incorrect username or password!"
            )

        if not verify_password(user_data.password, user.password_hash):
            raise HTTPException(
                status_code=401, detail="Incorrect username or password!"
            )
        payload = AccessTokenPayload(sub=user.id)
        access_token = create_access_token(payload)
        response.set_cookie("access_token", access_token)

    async def get_current_user(self, user_id: UUID) -> UserSchema:
        """
        Get current user
        :param user_id: - user id
        :return: - user
        """
        user = await UserRepository(self.session).get_one(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found!")
        return user

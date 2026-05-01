from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.services import BaseService
from src.user.schemas import UserSchema
from src.user.repository import UserRepository


class UserService(BaseService):

    def __init__(self, session: AsyncSession, user_repository: UserRepository):
        super().__init__(session)
        self.user_repository = user_repository

    async def get_user(self, user_id: UUID) -> UserSchema:
        """
        Get current user
        :param user_id: - user id
        :return: - user
        """
        user = await self.user_repository.get_one(id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

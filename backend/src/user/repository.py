from backend.src.core.base_repository import BaseRepository
from backend.src.user.model import UserOrm
from backend.src.user.schemas import UserSchema
from pydantic import BaseModel
from sqlalchemy import insert
from backend.src.user.security import hash_password


class UserRepository(BaseRepository[UserOrm, UserSchema]):
    model = UserOrm
    schema = UserSchema

    async def create(self, data_user: BaseModel) -> None:
        """
        Create user
        :param data_user: data for user creation
        :return: None
        """
        user_d = data_user.model_dump()
        user_d['password_hash'] = hash_password(user_d.pop('password'))
        statement = insert(self.model).values(**user_d).returning(self.model)
        await self.session.execute(statement)

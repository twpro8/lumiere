from src.core.repositories.base_data_mapper import BaseMapper
from src.user.models import UserOrm
from src.user.schemas import UserSchema


class UserMapper(BaseMapper[UserOrm, UserSchema]):
    orm_class = UserOrm
    schema_class = UserSchema

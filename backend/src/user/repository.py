from src.core.repositories import BaseRepository
from src.user.models import UserOrm
from src.user.schemas import UserSchema
from src.user.mappers import UserMapper


class UserRepository(BaseRepository[UserOrm, UserSchema]):
    model = UserOrm
    schema = UserSchema
    mapper = UserMapper

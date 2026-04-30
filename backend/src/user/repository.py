from src.core.repositories import BaseRepository
from src.user.models import UserOrm
from src.user.schemas import UserSchema


class UserRepository(BaseRepository[UserOrm, UserSchema]):
    model = UserOrm
    schema = UserSchema

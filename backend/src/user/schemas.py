from datetime import datetime
from uuid import UUID

from src.core.schemas import BaseSchema


class UserSchema(BaseSchema):
    id: UUID
    name: str
    username: str
    email: str
    password_hash: str
    avatar_url: str | None
    created_at: datetime

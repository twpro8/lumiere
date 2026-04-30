from datetime import datetime
from uuid import UUID

from src.core.schemas import BaseSchema


class UserSchema(BaseSchema):
    """
    Schema for get a user
    """

    id: UUID
    name: str
    username: str
    email: str
    password_hash: str
    avatar_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserReadSchema(BaseSchema):
    """
    Schema for get a user
    """

    id: UUID
    name: str
    username: str
    email: str
    avatar_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

from datetime import datetime
from uuid import UUID

from pydantic import EmailStr

from src.core.schemas import BaseSchema


class UserCreateRequestSchema(BaseSchema):
    """
    Schema for creating a user
    """

    name: str
    username: str
    email: EmailStr
    password: str


class UserCreateSchema(BaseSchema):
    """
    Schema for creating a user
    """

    name: str
    username: str
    email: str
    password_hash: str


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
    created_at: datetime


class UserLoginSchema(BaseSchema):
    """
    Schema for login a user
    """

    username: str
    password: str

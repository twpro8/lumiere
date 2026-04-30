from dataclasses import dataclass
from uuid import UUID

from pydantic import EmailStr

from src.core.schemas import BaseSchema


@dataclass
class AccessTokenPayload:
    sub: UUID


class UserCreateSchema(BaseSchema):
    """
    Schema for creating a user
    """

    name: str
    username: str
    email: str
    password_hash: str


class UserRegisterSchema(BaseSchema):
    """
    Schema for creating a user
    """

    name: str
    username: str
    email: EmailStr
    password: str


class UserLoginSchema(BaseSchema):
    """
    Schema for login a user
    """

    username: str
    password: str

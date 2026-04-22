from datetime import datetime
from backend.src.core.base_schema import BaseSchema
from pydantic import EmailStr


class UserCreateSchema(BaseSchema):
      """
      Schema for creating a user
      """
      name: str
      username: str
      email: EmailStr
      password: str
      created_at: datetime


class UserSchema(BaseSchema):
      """
      Schema for get a user
      """
      id: str
      name: str
      username: str
      email: EmailStr
      password_hash: str
      avatar_url: str | None
      created_at: datetime

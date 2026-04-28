from uuid import UUID

from pydantic import Field
from src.chat.model import ChatType
from src.core.postgres.types import created_at
from src.core.schemas import BaseSchema


class ChatSchema(BaseSchema):
    id: UUID
    created_at: created_at
    type: ChatType
    name: str | None
    photo_url: str | None


class ChatCreateSchema(BaseSchema):
    members_ids: list[UUID] = Field(min_length=2, max_length=9)
    name: str
    photo_url: str


# Members
class MemberSchema(BaseSchema):
    created_at: created_at
    user_id: UUID
    chat_id: UUID


class MemberCreateSchema(BaseSchema):
    user_id: UUID
    chat_id: UUID

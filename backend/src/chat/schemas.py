from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import Field

from src.core.schemas.base_schema import BaseSchema
from src.chat.enums import ChatType, ChatMemberRole


class ChatSchema(BaseSchema):
    id: UUID
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    type: ChatType

    # None for private chats
    image_url: str | None
    name: str | None
    description: str | None
    owner_id: UUID | None


class ChatCreateDBSchema(BaseSchema):
    type: ChatType = ChatType.private
    name: str | None = None
    description: str | None = None
    owner_id: UUID | None = None


class ChatCreateSchema(BaseSchema):
    members: Annotated[list[UUID], Field(min_length=2, max_length=9)]
    type: ChatType = ChatType.group
    name: str
    description: str


class MemberSchema(BaseSchema):
    chat_id: UUID
    user_id: UUID
    role: ChatMemberRole
    last_read_seq: int
    joined_at: datetime
    left_at: datetime | None

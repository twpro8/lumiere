from datetime import datetime
from uuid import UUID

from src.chat.enums import ChatMemberRole, ChatType
from src.core.schemas.base_schema import BaseSchema


class ChatSchema(BaseSchema):
    id: UUID
    type: ChatType
    name: str | None
    description: str | None
    owner_id: UUID | None
    image_url: str | None
    is_archived: bool
    created_at: datetime
    updated_at: datetime


class ChatMemberSchema(BaseSchema):
    chat_id: UUID
    user_id: UUID
    role: ChatMemberRole
    last_read_seq: int
    joined_at: datetime
    left_at: datetime | None

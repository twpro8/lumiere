from datetime import datetime
from uuid import UUID

from src.core.schemas.base_schema import BaseSchema


class MessageSchema(BaseSchema):

    chat_id: UUID | None
    channel_id: UUID | None
    sender_id: UUID
    body: str
    sequence: int
    parent_id: UUID | None
    is_edited: bool
    is_deleted: bool
    deleted_at: datetime | None
    created_at: datetime | None
    updated_at: datetime | None

from uuid import UUID

from src.core.postgres.types import created_at
from src.core.schemas import BaseSchema


class MessageSchema(BaseSchema):
    id: UUID
    author_id: UUID
    chat_id: UUID
    content: str
    created_at: created_at


class MessageCreateSchema(BaseSchema):
    chat_id: UUID
    content: str


# Will delete
class MessageCreateAuthSchema(MessageCreateSchema):
    author_id: UUID

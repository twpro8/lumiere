from uuid import UUID

from src.core.base_schema import BaseSchema
from src.postgres.types import created_at


class MessageSchema(BaseSchema):
    chat_id: UUID
    author_id: UUID
    content: str


class MessageSchemaDto(MessageSchema):
    id: UUID
    created_at: created_at

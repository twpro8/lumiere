from src.core.base_schema import BaseSchema
from src.postgres.types import created_at

from uuid import UUID

class MessageSchema(BaseSchema):
    chat_id: UUID
    author_id: UUID
    content: str

class MessageSchemaDto(MessageSchema):
    id: UUID
    created_at: created_at

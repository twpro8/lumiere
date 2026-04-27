from uuid import UUID

from src.core.postgres.types import created_at
from src.core.schemas import BaseSchema


class MessageSchema(BaseSchema):
    chat_id: UUID
    content: str

class MessageCreateSchema(MessageSchema):
    author_id: UUID

class MessageSchemaDto(MessageSchema):
    id: UUID
    created_at: created_at
    

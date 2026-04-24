from uuid import UUID

from src.chat.model import ChatType
from src.core.base_schema import BaseSchema
from src.postgres.types import created_at


class ChatSchema(BaseSchema):
    type: ChatType
    created_at: created_at


class ChatSchemaDTO(ChatSchema):
    id: UUID


class ChatSchemasResponse(BaseSchema):
    id: UUID
    chat_name: str | None
    photo_url: str | None
    created_at: created_at
    type: str

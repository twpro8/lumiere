from uuid import UUID

from src.chat.model import ChatType
from src.core.postgres.types import created_at
from src.core.schemas import BaseSchema


class ChatSchema(BaseSchema):
    type: ChatType
    created_at: created_at


class ChatSchemaDTO(ChatSchema):
    id: UUID


class CreateGroupChatSchema(BaseSchema):
    members_ids: list[UUID]
    name: str
    photo_url: str


# Response Schemas
class ChatSchemasResponse(BaseSchema):
    id: UUID
    name: str | None
    photo_url: str | None
    created_at: created_at
    type: str

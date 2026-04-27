from uuid import UUID

from pydantic import Field
from src.chat.model import ChatType
from src.core.postgres.types import created_at
from src.core.schemas import BaseSchema


class ChatSchema(BaseSchema):
    type: ChatType
    created_at: created_at


class ChatSchemaDTO(ChatSchema):
    id: UUID


class CreateGroupChatSchema(BaseSchema):
    members_ids: list[UUID] = Field(min_length=2, max_length=9)
    name: str
    photo_url: str


# Response Schemas
class ChatSchemasResponse(BaseSchema):
    id: UUID
    name: str | None
    photo_url: str | None
    created_at: created_at
    type: str

from src.core.base_schema import BaseSchema
from src.chat.model import ChatType
from src.postgres.types import created_at

from uuid import UUID

class ChatSchema(BaseSchema):
    type: ChatType
    created_at: created_at

class ChatSchemaDTO(ChatSchema):
    id: UUID

class CreateGroupChatSchema(BaseSchema):
    ...
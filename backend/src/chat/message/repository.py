from src.core.base_repository import BaseRepository
from src.chat.model import ChatMessageOrm
from src.chat.message.schemas import MessageSchema, MessageSchemaDto

from uuid import UUID

class MessageRepo(BaseRepository[ChatMessageOrm, MessageSchemaDto]):
    model = ChatMessageOrm
    schema = MessageSchemaDto
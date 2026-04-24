from uuid import UUID

from src.chat.message.schemas import MessageSchema, MessageSchemaDto
from src.chat.model import ChatMessageOrm
from src.core.base_repository import BaseRepository


class MessageRepo(BaseRepository[ChatMessageOrm, MessageSchemaDto]):
    model = ChatMessageOrm
    schema = MessageSchemaDto

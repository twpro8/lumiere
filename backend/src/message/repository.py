from src.core.repositories.base_repository import BaseRepository
from src.message.models import MessageOrm
from src.message.schemas import MessageSchema
from src.message.datamapper import MessageMapper


class MessageRepository(BaseRepository[MessageOrm, MessageSchema]):
    model = MessageOrm
    schema = MessageSchema
    mapper = MessageMapper

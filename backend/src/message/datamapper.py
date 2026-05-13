from src.core.repositories.base_data_mapper import BaseMapper
from src.message.schemas import MessageSchema
from src.message.models import MessageOrm


class MessageMapper(BaseMapper[MessageOrm, MessageSchema]):
    orm_class = MessageOrm
    schema_class = MessageSchema

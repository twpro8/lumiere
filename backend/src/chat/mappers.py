from src.core.repositories.base_data_mapper import BaseMapper
from src.chat.schemas import ChatSchema, ChatMemberSchema
from src.chat.models import ChatOrm, ChatMemberOrm


class ChatMapper(BaseMapper[ChatOrm, ChatSchema]):
    orm_class = ChatOrm
    schema_class = ChatSchema


class MemberMapper(BaseMapper[ChatMemberOrm, ChatMemberSchema]):
    orm_class = ChatMemberOrm
    schema_class = ChatMemberSchema

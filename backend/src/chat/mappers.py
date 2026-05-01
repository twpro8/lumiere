from src.core.repositories.base_data_mapper import BaseMapper
from src.chat.models import ChatMemberOrm, ChatOrm
from src.chat.schemas import MemberSchema, ChatSchema

class ChatMapper(BaseMapper[ChatOrm, ChatSchema]):
    orm_class = ChatOrm
    schema_class = ChatSchema

class MemberMapper(BaseMapper[ChatMemberOrm, MemberSchema]):
    orm_class = ChatMemberOrm
    schema_class = MemberSchema

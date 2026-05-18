from src.core.repositories.base_repository import BaseRepository
from src.chat.models import ChatOrm, ChatMemberOrm
from src.chat.schemas import ChatSchema, ChatMemberSchema
from src.chat.mappers import ChatMapper, MemberMapper


class ChatRepository(BaseRepository[ChatOrm, ChatSchema]):
    model = ChatOrm
    schema = ChatSchema
    mapper = ChatMapper


class MemberRepository(BaseRepository[ChatMemberOrm, ChatMemberSchema]):
    model = ChatMemberOrm
    schema = ChatMemberSchema
    mapper = MemberMapper

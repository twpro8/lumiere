from src.core.base_repository import BaseRepository
from src.chat.model import ChatMemberOrm, ChatOrm, ChatType
from src.chat.schemas import ChatSchemaDTO

from uuid import UUID

class ChatRepo(BaseRepository[ChatOrm, ChatSchemaDTO]):
    
    async def create_chat(self, type: ChatType) -> ChatOrm:
        """Create chat"""
        chat = ChatOrm(type=type) #!
        self.session.add(chat)
        await self.session.flush()
        return chat

    async def add_member(self, chat_id: UUID, user_id: UUID) -> ChatMemberOrm:
        """Add member to chat"""
        member = ChatMemberOrm(chat_id=chat_id, user_id=user_id)
        self.session.add(member)
        return member
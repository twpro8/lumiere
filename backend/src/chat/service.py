from src.core.base_service import BaseService
from src.chat.repository import ChatRepo
from src.chat.schemas import ChatSchema
from src.chat.model import ChatType

from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID

from pydantic import BaseModel
from datetime import datetime

class ChatListItemSchema(BaseModel):
    id: UUID
    type: ChatType
    created_at: datetime
    avatar_url: str | None
    username: str | None

class ChatService(BaseService):

    def __init__(self, chat_repo: ChatRepo, session: AsyncSession):
        super().__init__(session)
        self.chat_repo = chat_repo

    async def get_all_chats(self, user_id: UUID):
        """Get all user's chat"""
        return await self.chat_repo.get_all_chats(user_id)
    
    # Function for other service
    async def create_direct_chat(self, user_id1: UUID, user_id2: UUID):

        existing = await self.chat_repo.exist_dirrect_chat(user_id1=user_id1, user_id2=user_id2)
        
        if existing:

            return "Already exist"

        chat = await self.chat_repo.create_chat(type=ChatType.DIRECT)

        await self.chat_repo.add_member(chat_id=chat.id, user_id=user_id1)
        await self.chat_repo.add_member(chat_id=chat.id, user_id=user_id2)

        await self.session.commit()
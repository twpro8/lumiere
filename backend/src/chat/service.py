from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.chat.exceptions import DirectChatAlreadyExistException
from src.chat.model import ChatType
from src.chat.repository import ChatRepo
from src.core.base_service import BaseService


class ChatService(BaseService):

    def __init__(self, chat_repo: ChatRepo, session: AsyncSession):
        super().__init__(session)
        self.chat_repo = chat_repo

    async def get_all_chats(self, user_id: UUID):
        """Get all user's chat"""
        return await self.chat_repo.get_all_chats(user_id)

    # Function for other service
    async def create_direct_chat(self, user_id1: UUID, user_id2: UUID):

        existing = await self.chat_repo.dirrect_chat_exists(
            user_id1=user_id1, user_id2=user_id2
        )

        if existing:
            raise DirectChatAlreadyExistException

        chat = await self.chat_repo.create_chat(type=ChatType.DIRECT)

        await self.chat_repo.add_member(chat_id=chat.id, user_id=user_id1)
        await self.chat_repo.add_member(chat_id=chat.id, user_id=user_id2)

        await self.session.commit()

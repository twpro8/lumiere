from src.core.base_service import BaseService
from src.chat.message.repository import MessageRepo
from src.chat.message.schemas import MessageSchema

from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID

class MessageService(BaseService):

    def __init__(self, message_repo: MessageRepo, session: AsyncSession):
        super().__init__(session)
        self.message_repo = message_repo

    async def create_message(self, data: MessageSchema):
        """Create message"""
        response = await self.message_repo.create(data)
        await self.session.commit()
        return response

    async def get_messages_from_chat(self, chat_id: UUID, offset: int, limit: int = 10):
        """Get messages from chat"""
        return await self.message_repo.get_filtered(offset=offset, chat_id=chat_id, limit=limit)
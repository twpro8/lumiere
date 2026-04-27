from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from src.chat.exceptions import UserIsNotMemberOfChat
from src.chat.message.repository import MessageRepo
from src.chat.message.schemas import MessageSchema, MessageCreateSchema
from src.core.services import BaseService


class MessageService(BaseService):

    def __init__(self, message_repo: MessageRepo, session: AsyncSession):
        super().__init__(session)
        self.message_repo = message_repo

    async def create_message(self, data: MessageSchema, author_id: UUID):
        """Create message"""

        check_access = await self.message_repo.is_chat_member(
            user_id=author_id, chat_id=data.chat_id
        )

        if check_access is None:
            raise UserIsNotMemberOfChat

        new_data = MessageCreateSchema(content=data.content, chat_id=data.chat_id, author_id=author_id)

        response = await self.message_repo.create(new_data)
        await self.session.commit()
        return response

    async def get_messages_from_chat(self, chat_id: UUID, offset: int, limit: int = 10):
        """Get messages from chat"""

        return await self.message_repo.get_filtered(
            offset=offset, chat_id=chat_id, limit=limit
        )

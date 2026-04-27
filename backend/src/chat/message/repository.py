from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.chat.message.schemas import MessageSchema, MessageSchemaDto
from src.chat.model import ChatMemberOrm, ChatMessageOrm
from src.core.repositories import BaseRepository


class MessageRepo(BaseRepository[ChatMessageOrm, MessageSchemaDto]):
    model = ChatMessageOrm
    schema = MessageSchemaDto
    session: AsyncSession

    async def is_chat_member(self, chat_id: UUID, user_id: UUID):
        """Check if user is the member of chat"""

        query = select(ChatMemberOrm.id).filter_by(chat_id=chat_id, user_id=user_id)
        results = await self.session.execute(query)
        return results.scalar_one_or_none()
    


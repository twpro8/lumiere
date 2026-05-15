from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.chat.models import ChatOrm, ChatMemberOrm
from src.core.repositories.base_repository import BaseRepository
from src.message.models import MessageOrm
from src.message.schemas import MessageSchema
from src.message.datamapper import MessageMapper


class MessageRepository(BaseRepository[MessageOrm, MessageSchema]):
    model = MessageOrm
    schema = MessageSchema
    mapper = MessageMapper

    async def get_count_filtered(self, chat_id: UUID) -> int:

        stmt = select(func.count(MessageOrm.id)).where(MessageOrm.chat_id == chat_id)
        count = await self.session.scalar(stmt)

        if not count:
            raise ValueError

        return count

    async def check_chat_permission(self, chat_id: UUID, user_id: UUID) -> bool:

        data = await self.session.execute(
            select(ChatMemberOrm).filter_by(chat_id=chat_id, user_id=user_id)
        )
        if data.scalar():
            return True
        return False

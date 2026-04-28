from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.chat.message.schemas import MessageSchema, MessageSchema
from src.chat.model import ChatMemberOrm, ChatMessageOrm
from src.core.repositories import BaseRepository


class MessageRepo(BaseRepository[ChatMessageOrm, MessageSchema]):
    model = ChatMessageOrm
    schema = MessageSchema
    session: AsyncSession

    def _validate(self, obj: ChatMessageOrm) -> MessageSchema:
        return self.schema.model_validate(obj)

    def _validate_many(self, objs: Sequence[ChatMessageOrm]) -> list[MessageSchema]:
        return [self.schema.model_validate(obj) for obj in objs]

    async def is_chat_member(self, chat_id: UUID, user_id: UUID) -> bool:
        """Check if user is the member of chat"""

        query = select(ChatMemberOrm.id).filter_by(chat_id=chat_id, user_id=user_id)
        results = await self.session.execute(query)
        return results.scalar_one_or_none() is not None

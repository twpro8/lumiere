from typing import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.schemas.base_schema import BaseSchema
from src.chat.models import ChatMemberOrm, ChatOrm
from src.chat.enums import ChatMemberRole, ChatType
from src.core.postgres import UUIDBase
from src.chat.schemas import ChatSchema, MemberSchema, ChatCreateSchema
from src.core.repositories.base_repository import BaseRepository
from src.chat.mappers import ChatMapper, MemberMapper
from src.chat.sql_requests import get_all_chats_sql


class ChatRepository(BaseRepository[ChatOrm, ChatSchema]):
    schema = ChatSchema
    model = ChatOrm
    mapper = ChatMapper

    async def get_all_chats(self, user_id: UUID) -> Sequence[ChatSchema]:
        """Gets all chats in the database"""

        result = await self.session.execute(get_all_chats_sql, {"user_id": user_id})
        chats = result.mappings().all()

        return [self.mapper.to_schema(ChatOrm(**chat)) for chat in chats]


class MemberRepository(BaseRepository[ChatMemberOrm, MemberSchema]):
    schema = MemberSchema
    model = ChatMemberOrm
    mapper = MemberMapper

    async def add_members(
        self, members: list[UUID], chat_id: UUID, owner_id: UUID | None
    ) -> None:
        """Create list of new members with the given user_id and chat_id"""

        orm_members = [
            ChatMemberOrm(user_id=user_id, chat_id=chat_id, role=ChatMemberRole.member)
            for user_id in members
        ]
        if owner_id:
            orm_members.append(
                ChatMemberOrm(
                    user_id=owner_id, chat_id=chat_id, role=ChatMemberRole.owner
                )
            )

        self.session.add_all(orm_members)
        await self.session.flush()

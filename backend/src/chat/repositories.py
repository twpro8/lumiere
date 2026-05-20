from uuid import UUID

from sqlalchemy import and_, insert, select
from sqlalchemy.orm import aliased

from src.core.repositories.base_repository import BaseRepository
from src.chat.models import ChatOrm, ChatMemberOrm
from src.chat.schemas import ChatSchema, ChatMemberSchema, MemberCreateSchema
from src.chat.mappers import ChatMapper, MemberMapper
from src.chat.enums import ChatMemberRole, ChatType


class ChatRepository(BaseRepository[ChatOrm, ChatSchema]):
    model = ChatOrm
    schema = ChatSchema
    mapper = ChatMapper

    async def find_private_chat(self, user_a: UUID, user_b: UUID) -> ChatSchema | None:
        """Find private chat beetween users"""

        member_a = aliased(ChatMemberOrm)
        member_b = aliased(ChatMemberOrm)

        query = (
            select(ChatOrm)
            .join(
                member_a,
                and_(member_a.chat_id == ChatOrm.id, member_a.user_id == user_a),
            )
            .join(
                member_b,
                and_(member_b.chat_id == ChatOrm.id, member_b.user_id == user_b),
            )
            .where(ChatOrm.type == ChatType.private)
        )

        return await self._execute_and_map_one_or_none(query)


class MemberRepository(BaseRepository[ChatMemberOrm, ChatMemberSchema]):
    model = ChatMemberOrm
    schema = ChatMemberSchema
    mapper = MemberMapper

    async def add_members(self, members: list[MemberCreateSchema]) -> None:
        statement = insert(ChatMemberOrm).values([m.model_dump() for m in members])
        await self.session.execute(statement)

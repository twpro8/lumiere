from typing import Sequence
from uuid import UUID

from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.testing.pickleable import User
from src.chat.enums import ChatMemberRole, ChatType
from src.chat.mappers import ChatMapper, MemberMapper
from src.chat.models import ChatMemberOrm, ChatOrm
from src.chat.schemas import ChatCreateSchema, ChatSchema, MemberSchema
from src.core.postgres import UUIDBase
from src.core.repositories.base_repository import BaseRepository
from src.core.schemas.base_schema import BaseSchema
from src.user.models import UserOrm


class ChatRepository(BaseRepository[ChatOrm, ChatSchema]):
    schema = ChatSchema
    model = ChatOrm
    mapper = ChatMapper

    async def get_all_chats(
        self, user_id: UUID, limit: int = 20, offset: int = 0
    ) -> Sequence[ChatSchema]:
        """Get all chats with the given user_id"""

        cm = aliased(ChatMemberOrm)
        cc = aliased(ChatMemberOrm)
        u = aliased(UserOrm)

        chat_name = case((ChatOrm.type == "private", u.name), else_=ChatOrm.name).label(
            "name"
        )

        chat_image = case(
            (ChatOrm.type == "private", u.avatar_url), else_=ChatOrm.image_url
        ).label("image_url")

        query = (
            select(
                ChatOrm.id,
                ChatOrm.updated_at,
                ChatOrm.is_archived,
                ChatOrm.description,
                ChatOrm.owner_id,
                ChatOrm.created_at,
                ChatOrm.type,
                chat_name,
                chat_image,
            )
            .distinct(ChatOrm.id)
            .join(cm, (cm.chat_id == ChatOrm.id) & (cm.user_id == user_id))
            .outerjoin(
                cc,
                (cc.chat_id == ChatOrm.id)
                & (cc.user_id != user_id)
                & (ChatOrm.type == "private"),
            )
            .outerjoin(u, u.id == cc.user_id)
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)
        return [
            self.mapper.to_schema(ChatOrm(**row)) for row in result.mappings().all()
        ]


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

    async def check_user_is_member(self, chat_id: UUID, user_id: UUID) -> bool:
        data = await self.session.execute(
            select(ChatMemberOrm).filter(
                ChatMemberOrm.chat_id == chat_id, ChatMemberOrm.user_id == user_id
            )
        )
        result = data.scalar_one_or_none()

        return result is not None

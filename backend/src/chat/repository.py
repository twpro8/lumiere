from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import text
from src.chat.model import ChatMemberOrm, ChatOrm, ChatType
from src.chat.schemas import ChatSchema, MemberSchema
from src.core.repositories import BaseRepository


class ChatRepository(BaseRepository[ChatOrm, ChatSchema]):

    def _validate(self, obj: ChatOrm) -> ChatSchema:
        return self.schema.model_validate(obj)

    def _validate_many(self, objs: Sequence[Any]) -> list[ChatSchema]:
        return [self.schema.model_validate(obj) for obj in objs]

    async def create_direct_chat(self) -> ChatSchema:
        """Create dirrect chat"""

        chat = ChatOrm(type=ChatType.DIRECT)  #!
        self.session.add(chat)
        await self.session.flush()
        return self._validate(chat)

    async def create_group_chat(
        self, owner_id: UUID, name: str, photo_url: str
    ) -> ChatSchema:
        """Create group chat"""

        chat = ChatOrm(
            type=ChatType.GROUP, name=name, photo_url=photo_url, owner_id=owner_id
        )
        self.session.add(chat)
        await self.session.flush()
        return self._validate(chat)

    async def dirrect_chat_exists(self, user_id1: UUID, user_id2: UUID) -> None | UUID:
        """Check if direct chat between users alredy exist"""

        query = text("""
            SELECT c.id FROM chats c
            JOIN chats_members cm1 ON cm1.chat_id = c.id AND cm1.user_id = :user_id1
            JOIN chats_members cm2 ON cm2.chat_id = c.id AND cm2.user_id = :user_id2
            WHERE c.type = 'DIRECT'
            LIMIT 1
""")
        result = await self.session.execute(
            query,
            {
                "user_id1": str(user_id1),
                "user_id2": str(user_id2),
            },
        )

        return result.scalar_one_or_none()

    async def get_all_chats(self, user_id: UUID) -> list[ChatSchema]:
        """Get all chats via sql"""

        query = text("""
                    select
                    	c.id,
                    	c.created_at,
                        c.type,
                    	case when c.type = 'DIRECT' then u.username else c.name end as name,
                    	case when c.type = 'DIRECT' then u.avatar_url else c.photo_url end as photo_url
                    from chats c
                    join chats_members cm on cm.chat_id = c.id and cm.user_id = :user_id
                    join chats_members ca on cm.chat_id = ca.chat_id
                    join users u on u.id = ca.user_id and ca.user_id != :user_id
                     """)

        data = await self.session.execute(query, {"user_id": str(user_id)})
        return self._validate_many(data.mappings().all())


class MemberRepository(BaseRepository[ChatMemberOrm, MemberSchema]):

    def _validate(self, obj: ChatMemberOrm) -> MemberSchema:
        return self.schema.model_validate(obj)

    def _validate_many(self, objs: Sequence[ChatMemberOrm]) -> list[MemberSchema]:
        return [self.schema.model_validate(obj) for obj in objs]

    async def add_member(self, chat_id: UUID, user_id: UUID) -> MemberSchema:
        """Add member to chat"""

        member = ChatMemberOrm(chat_id=chat_id, user_id=user_id)
        self.session.add(member)
        await self.session.flush()
        return self._validate(member)

    async def bulk_add_members(
        self, chat_id: UUID, user_ids: list[UUID]
    ) -> list[MemberSchema]:
        """Add a lot of members in 1 request"""

        members = [
            ChatMemberOrm(chat_id=chat_id, user_id=user_id) for user_id in user_ids
        ]
        self.session.add_all(members)

        return self._validate_many(members)

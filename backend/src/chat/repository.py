from uuid import UUID

from sqlalchemy import text

from src.chat.model import ChatMemberOrm, ChatOrm, ChatType
from src.chat.schemas import ChatSchemaDTO
from src.core.base_repository import BaseRepository


class ChatRepo(BaseRepository[ChatOrm, ChatSchemaDTO]):

    async def create_chat(self, chat_type: ChatType) -> ChatOrm:
        """Create chat"""
        chat = ChatOrm(type=chat_type)  #!
        self.session.add(chat)
        await self.session.flush()
        return chat

    async def add_member(self, chat_id: UUID, user_id: UUID) -> ChatMemberOrm:
        """Add member to chat"""
        member = ChatMemberOrm(chat_id=chat_id, user_id=user_id)
        self.session.add(member)
        return member

    async def dirrect_chat_exists(self, user_id1: UUID, user_id2: UUID):
        """Check if dirrect chat between users alredy exist"""

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

    async def get_all_chats(self, user_id: UUID):
        """Get all chats via sql"""

        query = text("""
                    select 
                    	c.id, 
                    	c.created_at,
                        c.type,
                    	case when c.type = 'DIRECT' then u.username else c.name end as chat_name,
                    	case when c.type = 'DIRECT' then u.avatar_url else c.photo_url end as photo_url
                    from chats c
                    join chats_members cm on cm.chat_id = c.id and cm.user_id = :user_id
                    join chats_members ca on cm.chat_id = ca.chat_id
                    join users u on u.id = ca.user_id and ca.user_id != :user_id
                     """)

        data = await self.session.execute(query, {"user_id": str(user_id)})
        return data.mappings().all()

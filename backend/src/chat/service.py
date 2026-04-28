from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from src.chat.exceptions import DirectChatAlreadyExistException
from src.chat.repository import ChatRepository, MemberRepository
from src.chat.schemas import ChatCreateSchema, ChatSchema
from src.core.services import BaseService


class ChatService(BaseService):

    def __init__(
        self,
        chat_repo: ChatRepository,
        member_repo: MemberRepository,
        session: AsyncSession,
    ):
        super().__init__(session)
        self.chat_repo = chat_repo
        self.member_repo = member_repo

    async def get_all_chats(self, user_id: UUID) -> list[ChatSchema]:
        """Get all user's chat (By user_id)"""

        return await self.chat_repo.get_all_chats(user_id)

    async def create_group_chat(
        self, owner_id: UUID, data: ChatCreateSchema
    ) -> ChatSchema:
        """Create Group chat"""

        chat = await self.chat_repo.create_group_chat(
            **data.model_dump(exclude={"members_ids"}), owner_id=owner_id
        )

        members_ids = [*data.members_ids, owner_id]

        await self.member_repo.bulk_add_members(chat_id=chat.id, user_ids=members_ids)

        await self.session.commit()

        return chat

    # Function for other service
    async def create_direct_chat(self, user_id1: UUID, user_id2: UUID) -> ChatSchema:
        """Create dirrect chat between 2 users"""
        existing = await self.chat_repo.dirrect_chat_exists(
            user_id1=user_id1, user_id2=user_id2
        )

        if existing:
            raise DirectChatAlreadyExistException

        chat = await self.chat_repo.create_direct_chat()

        await self.member_repo.add_member(chat_id=chat.id, user_id=user_id1)
        await self.member_repo.add_member(chat_id=chat.id, user_id=user_id2)

        await self.session.commit()

        return chat

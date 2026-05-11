from typing import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.chat.repository import ChatRepository, MemberRepository
from src.chat.schemas import ChatCreateDBSchema, ChatCreateSchema, ChatSchema
from src.core.services.base_service import BaseService


class ChatService(BaseService):

    def __init__(
        self,
        chat_repository: ChatRepository,
        member_repository: MemberRepository,
        session: AsyncSession,
    ) -> None:

        super().__init__(session)
        self.chat_repository = chat_repository
        self.member_repository = member_repository

    async def create_chat(self, data: ChatCreateSchema, owner_id: UUID) -> ChatSchema:
        """Creates a new group chat"""

        chat = await self.chat_repository.create(
            ChatCreateDBSchema.model_validate(
                {**data.model_dump(), "owner_id": owner_id}
            )
        )

        await self.member_repository.add_members(
            chat_id=chat.id, members=data.members, owner_id=owner_id
        )
        await self.session.commit()

        return chat

    async def get_all_chats(self, user_id: UUID, offset: int) -> Sequence[ChatSchema]:
        """Gets all chats belonging to a user"""

        chats = await self.chat_repository.get_all_chats(user_id, offset=offset)
        return chats

    async def get_chat(self, chat_id: UUID) -> ChatSchema | None:
        """Gets a chat by its id"""

        chat = await self.chat_repository.get_one(id=chat_id)
        return chat

    # for other service
    async def create_private_chat(self, user_id_1: UUID, user_id_2: UUID) -> ChatSchema:
        """Creates a new private chat"""
        chat = await self.chat_repository.create(ChatCreateDBSchema())
        await self.member_repository.add_members(
            chat_id=chat.id, members=[user_id_1, user_id_2], owner_id=None
        )
        await self.session.commit()
        return chat

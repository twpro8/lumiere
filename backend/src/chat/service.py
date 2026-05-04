from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.chat.schemas import CreateChatSchema, ChatSchema
from src.core.services.base_service import BaseService
from src.chat.repository import ChatRepository, MemberRepository


class ChatService(BaseService):

    def __init__(self, chat_repo: ChatRepository, member_repo: MemberRepository, session: AsyncSession) -> None:
        self.chat_repo = chat_repo
        self.member_repo = member_repo
        self.session = session

    async def create_chat(self, data: CreateChatSchema, owner_id: UUID) -> ChatSchema:
        """Creates a new group chat"""

        chat = await self.chat_repo.create_group_chat(data, owner_id)

        await self.member_repo.add_members(chat_id=chat.id, members=data.members, owner_id=owner_id)
        await self.session.commit()

        return chat
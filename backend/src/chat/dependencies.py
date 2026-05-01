from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.chat.repository import ChatRepository, MemberRepository
from src.chat.service import ChatService
from src.core.postgres.session import get_session


async def get_chat_service(session: AsyncSession = Depends(get_session), ) -> ChatService:
    member_repo = MemberRepository(session)
    chat_repo = ChatRepository(session)
    return ChatService(session=session, chat_repo=chat_repo, member_repo=member_repo)

ChatDepends = Annotated[ChatService, Depends(get_chat_service)]

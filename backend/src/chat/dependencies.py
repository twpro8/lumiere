from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.chat.repository import ChatRepository, MemberRepository
from src.chat.service import ChatService
from src.core.postgres.session import get_session


def get_chat_repo(session: AsyncSession = Depends(get_session)) -> ChatRepository:
    return ChatRepository(session=session)


def get_member_repo(session: AsyncSession = Depends(get_session)) -> MemberRepository:
    return MemberRepository(session=session)


def get_chat_service(
    chat_repo: ChatRepository = Depends(get_chat_repo),
    member_repo: MemberRepository = Depends(get_member_repo),
    session: AsyncSession = Depends(get_session),
) -> ChatService:
    return ChatService(chat_repo=chat_repo, member_repo=member_repo, session=session)


ChatRepoDep = Annotated[ChatRepository, Depends(get_chat_repo)]
ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]

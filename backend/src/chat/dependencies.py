from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.chat.repository import ChatRepository, MemberRepository
from src.chat.service import ChatService
from src.core.dependencies import SessionDep


def get_chat_repository(
    session: SessionDep,
) -> ChatRepository:
    return ChatRepository(session)


def get_member_repository(
    session: SessionDep,
) -> MemberRepository:
    return MemberRepository(session)


def get_chat_service(
    session: SessionDep,
    chat_repository: ChatRepositoryDep,
    member_repository: MemberRepositoryDep,
) -> ChatService:

    return ChatService(
        session=session,
        chat_repository=chat_repository,
        member_repository=member_repository,
    )


ChatRepositoryDep = Annotated[ChatRepository, Depends(get_chat_repository)]
MemberRepositoryDep = Annotated[MemberRepository, Depends(get_member_repository)]
ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]

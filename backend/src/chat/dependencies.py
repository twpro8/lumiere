from typing import Annotated, AsyncGenerator

from fastapi import Depends

from src.chat.repositories import ChatRepository, MemberRepository
from src.chat.unit_of_work import ChatUnitOfWork
from src.core.dependencies import SessionDep
from src.chat.service import ChatService


def get_chat_repository(session: SessionDep) -> ChatRepository:
    return ChatRepository(session)


def get_chat_member_repository(session: SessionDep) -> MemberRepository:
    return MemberRepository(session)


def get_chat_service(unit_of_work: ChatUnitOfWorkDep) -> ChatService:
    return ChatService(unit_of_work)


async def get_chat_unit_of_work(
    session: SessionDep,
    chat_repository: ChatRepositoryDep,
    chat_member_repository: ChatMemberRepository,
) -> AsyncGenerator[ChatUnitOfWork]:
    async with ChatUnitOfWork(
        session=session,
        chat_repository=chat_repository,
        chat_member_repository=chat_member_repository,
    ) as unit_of_work:
        yield unit_of_work


ChatRepositoryDep = Annotated[ChatRepository, Depends(get_chat_repository)]
ChatMemberRepository = Annotated[MemberRepository, Depends(get_chat_member_repository)]
ChatUnitOfWorkDep = Annotated[ChatUnitOfWork, Depends(get_chat_unit_of_work)]
ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]

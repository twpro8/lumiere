from typing import Annotated, AsyncGenerator

from fastapi import Depends

from src.chat.repositories import ChatRepository
from src.chat.unit_of_work import ChatUnitOfWork
from src.core.dependencies import SessionDep


def get_chat_repository(session: SessionDep) -> ChatRepository:
    return ChatRepository(session)


async def get_chat_unit_of_work(
    session: SessionDep,
    chat_repository: ChatRepositoryDep,
) -> AsyncGenerator[ChatUnitOfWork]:
    async with ChatUnitOfWork(session, chat_repository) as unit_of_work:
        yield unit_of_work


ChatRepositoryDep = Annotated[ChatRepository, Depends(get_chat_repository)]
ChatUnitOfWorkDep = Annotated[ChatUnitOfWork, Depends(get_chat_unit_of_work)]

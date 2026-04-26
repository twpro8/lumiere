from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.chat.message.repository import MessageRepo
from src.chat.message.service import MessageService
from src.core.postgres.session import get_session


def get_message_repo(session: AsyncSession = Depends(get_session)) -> MessageRepo:
    return MessageRepo(session=session)


def get_message_service(
    repo: MessageRepo = Depends(get_message_repo),
    session: AsyncSession = Depends(get_session),
) -> MessageService:
    return MessageService(message_repo=repo, session=session)


MessageRepoDep = Annotated[MessageRepo, Depends(get_message_repo)]
MessageServiceDep = Annotated[MessageService, Depends(get_message_service)]

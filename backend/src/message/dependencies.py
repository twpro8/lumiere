from fastapi import Depends

from src.core.dependencies import SessionDep
from src.message.repository import MessageRepository
from src.message.service import MessageService

from typing import Annotated


def get_message_repository(session: SessionDep) -> MessageRepository:
    return MessageRepository(session)


def get_message_service(
    session: SessionDep, repository: MessageRepositoryDep
) -> MessageService:
    return MessageService(session, repository)


MessageRepositoryDep = Annotated[MessageRepository, Depends(get_message_repository)]
MessageServiceDep = Annotated[MessageService, Depends(get_message_service)]

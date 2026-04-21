
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.postgres.session import get_session
from src.chat.repository import ChatRepo
from src.chat.service import ChatService


def get_chat_repo(session: AsyncSession = Depends(get_session)) -> ChatRepo:
    return ChatRepo(session=session)


def get_chat_service(repo: ChatRepo = Depends(get_chat_repo), session: AsyncSession = Depends(get_session)) -> ChatService:
    return ChatService(chat_repo=repo, session=session)

ChatRepoDep = Annotated[ChatRepo, Depends(get_chat_repo)]
ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
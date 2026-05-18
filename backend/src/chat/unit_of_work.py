from sqlalchemy.ext.asyncio import AsyncSession

from src.core.unit_of_work import BaseUnitOfWork
from src.chat.repositories import ChatRepository


class ChatUnitOfWork(BaseUnitOfWork):
    def __init__(self, session: AsyncSession, chat_repository: ChatRepository):
        super().__init__(session)
        self.chats = chat_repository

    def _uow_marker(self) -> None: ...

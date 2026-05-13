from sqlalchemy.ext.asyncio import AsyncSession

from src.core.services.base_service import BaseService
from src.message.repository import MessageRepository


class MessageService(BaseService):

    def __init__(
        self,
        session: AsyncSession,
        message_repository: MessageRepository,
    ):
        super().__init__(session=session)
        self.message_repository = message_repository

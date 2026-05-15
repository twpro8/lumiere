from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.services.base_service import BaseService
from src.message.repository import MessageRepository
from src.message.schemas import (
    MessageSchema,
    CreateMessageSchema,
    CreateChatMessageSchema,
    CreateChannelMessageSchema,
)
from src.message.exceptions import ChatPermissionException


class MessageService(BaseService):

    def __init__(
        self,
        session: AsyncSession,
        message_repository: MessageRepository,
    ):
        super().__init__(session=session)
        self.message_repository = message_repository

    async def create_message_in_chat(
        self,
        chat_id: UUID,
        data: CreateMessageSchema,
        sender_id: UUID,
    ) -> MessageSchema:

        check_permission = await self.message_repository.check_chat_permission(
            chat_id=chat_id, user_id=sender_id
        )
        if check_permission is None:
            raise ChatPermissionException

        sequence = await self.message_repository.get_count_filtered(chat_id=chat_id)

        message = await self.message_repository.create(
            CreateChatMessageSchema(
                **data.model_dump(),
                chat_id=chat_id,
                sender_id=sender_id,
                sequence=sequence + 1
            )
        )

        await self.session.commit()

        return message

    async def create_message_in_channel(
        self,
        channel_id: UUID,
        data: CreateMessageSchema,
        sender_id: UUID,
    ) -> MessageSchema:

        message = await self.message_repository.create(
            CreateChannelMessageSchema(
                **data.model_dump(), sender_id=sender_id, channel_id=channel_id
            )
        )

        await self.session.commit()

        return message

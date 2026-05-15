from uuid import UUID

from fastapi import APIRouter

from src.message.schemas import MessageSchema, CreateMessageSchema
from src.message.dependencies import MessageServiceDep
from src.message.enums import MessageType

router = APIRouter(
    prefix="/messages",
)


@router.post("/{recipient}", response_model=MessageSchema)
async def create_message(
    service: MessageServiceDep,
    message: CreateMessageSchema,
    sender_id: UUID,
    recipient: UUID,
    message_type: MessageType,
) -> MessageSchema:
    """Create a new message. recipient: UUID (chat or channel ID)"""

    if message_type == MessageType.CHAT:
        return await service.create_message_in_chat(
            chat_id=recipient, data=message, sender_id=sender_id
        )

    elif message_type == MessageType.CHANNEL:
        return await service.create_message_in_channel(
            channel_id=recipient, data=message, sender_id=sender_id
        )

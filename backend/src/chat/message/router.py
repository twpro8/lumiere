from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from src.chat.message.dependencies import MessageServiceDep
from src.chat.message.schemas import MessageSchema, MessageCreateSchema

router = APIRouter(prefix="/chats/messages", tags=["Chat Messages"])


@router.post("/", response_model=MessageSchema)
async def create_message(
    service: MessageServiceDep, data: MessageCreateSchema, author_id: UUID
) -> MessageSchema:
    """Create message"""

    return await service.create_message(data, author_id)


@router.get("/", response_model=list[MessageSchema])
async def get_messages(
    service: MessageServiceDep, chat_id: UUID, offset: int = 0
) -> Sequence[MessageSchema]:
    """Get messages from chat"""

    return await service.get_messages_from_chat(offset=offset, chat_id=chat_id)

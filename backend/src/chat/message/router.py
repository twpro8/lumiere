from uuid import UUID

from fastapi import APIRouter, Depends
from src.chat.message.dependencies import MessageServiceDep
from src.chat.message.schemas import MessageSchema, MessageSchemaDto

router = APIRouter(prefix="/chat/message", tags=["chats_messages"])


@router.post("/create", response_model=MessageSchemaDto)
async def create_chat(service: MessageServiceDep, data: MessageSchema):
    """Create message"""

    return await service.create_message(data)


@router.get("/get_all", response_model=list[MessageSchemaDto])
async def get_messages(service: MessageServiceDep, chat_id: UUID, offset: int = 0):
    """Get messages from chat"""

    return await service.get_messages_from_chat(offset=offset, chat_id=chat_id)

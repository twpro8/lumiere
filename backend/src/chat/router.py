from fastapi import APIRouter

from src.chat.dependencies import ChatServiceDep
from src.chat.schemas import ChatCreateRequestSchema
from src.user.dependencies import UserIdDep

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.post("")
async def create_chat(
    current_user_id: UserIdDep,
    service: ChatServiceDep,
    data: ChatCreateRequestSchema,
) -> ChatCreateRequestSchema:
    await service.create_chat(current_user_id, data)
    return data

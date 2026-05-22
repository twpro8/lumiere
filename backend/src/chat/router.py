from fastapi import APIRouter, HTTPException, status

from src.chat.dependencies import ChatServiceDep
from src.chat.schemas import ChatCreateRequestSchema
from src.user.dependencies import UserIdDep
from src.chat.exceptions import SelfChatCreationNotAllowed

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_chat(
    current_user_id: UserIdDep,
    service: ChatServiceDep,
    data: ChatCreateRequestSchema,
) -> ChatCreateRequestSchema:
    try:
        await service.create_chat(current_user_id, data)
    except SelfChatCreationNotAllowed as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    return data

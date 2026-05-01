from fastapi import APIRouter

from src.chat.schemas import CreateChatSchema, ChatSchema
from src.chat.dependencies import ChatDepends
from src.user.dependencies import UserIdDep

router = APIRouter(prefix="/chats", tags=["chat"])


@router.post("/", response_model=ChatSchema)
async def create_chat(service: ChatDepends, data: CreateChatSchema, owner_id: UserIdDep) -> ChatSchema:
    return await service.create_chat(data=data, owner_id=owner_id)

from uuid import UUID

from fastapi import APIRouter

from src.chat.dependencies import ChatServiceDep
from src.chat.schemas import ChatSchemasResponse

router = APIRouter(prefix="/chat", tags=["chats"])


@router.post("/create")
async def create_chat(service: ChatServiceDep, id1, id2):
    """will delete"""
    return await service.create_direct_chat(user_id1=id1, user_id2=id2)


@router.get("/get_all", response_model=list[ChatSchemasResponse])
async def get_chats(service: ChatServiceDep, user_id: UUID):
    """Get all user's chats"""
    return await service.get_all_chats(user_id=user_id)

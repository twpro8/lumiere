from uuid import UUID

from fastapi import APIRouter

from src.chat.dependencies import ChatServiceDep
from src.chat.schemas import ChatSchema, ChatCreateSchema

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get(
    "/",
    response_model=list[ChatSchema],
    description="Get all user's chats",
)
async def get_chats(
    service: ChatServiceDep, user_id: UUID
) -> list[ChatSchema]:  # Change getting user_id to getting it from the service
    """Get all user's chats"""

    return await service.get_all_chats(user_id=user_id)


@router.post("/", response_model=ChatSchema, description="Create group chat")
async def create_chat(
    service: ChatServiceDep, owner_id: UUID, data: ChatCreateSchema
) -> ChatSchema:  # Change getting user_id to getting it from the service
    """Create group chat"""

    return await service.create_group_chat(owner_id=owner_id, data=data)


# Will delete
@router.post("/create_direct")
async def create_chat_dir(service: ChatServiceDep, id1: UUID, id2: UUID) -> ChatSchema:
    return await service.create_direct_chat(user_id1=id1, user_id2=id2)

from typing import Sequence

from fastapi import APIRouter

from uuid import UUID

from src.chat.schemas import ChatCreateSchema, ChatSchema
from src.chat.dependencies import ChatServiceDep
from src.user.dependencies import UserIdDep

router = APIRouter(prefix="/chats", tags=["chat"])


@router.post("", response_model=ChatSchema)
async def create_chat(
    service: ChatServiceDep,
    data: ChatCreateSchema,
    owner_id: UserIdDep,
) -> ChatSchema:
    return await service.create_chat(data=data, owner_id=owner_id)


@router.get("")
async def get_all_chats(
    service: ChatServiceDep,
    user_id: UserIdDep,
    offset: int = 0,
) -> Sequence[ChatSchema]:
    return await service.get_all_chats(user_id=user_id, offset=offset)


# Will delete
@router.post("/create/private", response_model=ChatSchema)
async def create_private_chat(
    service: ChatServiceDep,
    user_id_1: UUID,
    users_id_2: UUID,
) -> ChatSchema:
    return await service.create_private_chat(user_id_1=user_id_1, user_id_2=users_id_2)

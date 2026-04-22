from fastapi import APIRouter, Depends
from src.chat.dependencies import ChatServiceDep

router = APIRouter(prefix="/chat")

@router.post("/create")
async def create_chat(service: ChatServiceDep, id1, id2):
    """will delete"""
    return await service.create_chat(user_id1=id1, user_id2=id2)
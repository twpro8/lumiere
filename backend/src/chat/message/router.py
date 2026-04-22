from fastapi import APIRouter, Depends
from src.chat.message.dependencies import MessageServiceDep
from src.chat.message.schemas import MessageSchema

router = APIRouter(prefix="/message")

@router.post("/create")
async def create_chat(service: MessageServiceDep, data: MessageSchema):
    """Create message"""
    return await service.create_message(data)
from fastapi import APIRouter
from backend.src.core.dependencies import SessionDep
from backend.src.user.schemas import UserCreateSchema
from backend.src.user.repository import UserRepository

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", summary='Register new user')
async def register_user(user_data: UserCreateSchema, session: SessionDep) -> dict[str, str]:
    """Register new user"""
    await UserRepository(session).create(user_data)
    await session.commit()
    return {'detail': 'User successfully created!'}

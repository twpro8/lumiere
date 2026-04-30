from fastapi import APIRouter

from src.user.schemas import UserReadSchema
from src.user.dependencies import CurrentUserDep

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    summary="Get current user",
    response_model=UserReadSchema,
)
async def get_current_user(
    user: CurrentUserDep,
) -> UserReadSchema:
    """Get current user"""
    return UserReadSchema.model_validate(user)

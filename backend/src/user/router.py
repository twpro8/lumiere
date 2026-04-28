from fastapi import APIRouter, Response

from src.core.schemas import SuccessResponse
from src.user.schemas import (
    UserCreateRequestSchema,
    UserLoginSchema,
    UserReadSchema,
)
from src.user.dependencies import (
    UserServiceDep,
    CurrentUserDep,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", summary="Register new user", response_model=SuccessResponse)
async def register_user(
    user_data: UserCreateRequestSchema,
    service: UserServiceDep,
) -> None:
    """Register new user"""
    await service.create_user(user_data)


@router.post("/login", summary="Login user", response_model=SuccessResponse)
async def login_user(
    data_login: UserLoginSchema,
    response: Response,
    service: UserServiceDep,
) -> None:
    """Login user"""
    access_token = await service.authenticate_user(data_login)
    response.set_cookie("access_token", access_token)


@router.get("/me", summary="Get current user", response_model=UserReadSchema)
async def get_current_user(
    user: CurrentUserDep,
) -> UserReadSchema:
    """Get current user"""
    return UserReadSchema.model_validate(user)

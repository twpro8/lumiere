from fastapi import APIRouter, Response, status

from src.auth.dependencies import AuthServiceDep
from src.core.config import settings
from src.core.schemas import SuccessResponse
from src.auth.schemas import (
    UserRegisterSchema,
    UserLoginSchema,
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post(
    "/register",
    summary="Register new user",
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user_data: UserRegisterSchema,
    service: AuthServiceDep,
) -> SuccessResponse:
    """Register new user"""
    await service.create_user(user_data)
    return SuccessResponse()


@router.post(
    "/login",
    summary="Login user",
)
async def login_user(
    data_login: UserLoginSchema,
    response: Response,
    service: AuthServiceDep,
) -> SuccessResponse:
    """Login user"""
    access_token = await service.authenticate_user(data_login)
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    return SuccessResponse()

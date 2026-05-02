from fastapi import APIRouter, Response, status

from src.auth.dependencies import AuthServiceDep
from src.auth.utils import set_tokens_cookie
from src.core.schemas import SuccessResponse
from src.core.dependencies import RefreshTokenDep
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
    tokens = await service.authenticate_user(data_login)
    set_tokens_cookie(response, tokens.access_token, tokens.refresh_token)
    return SuccessResponse()


@router.post("/refresh", summary="Refresh token")
async def refresh(
    service: AuthServiceDep,
    response: Response,
    refresh_token: RefreshTokenDep,
) -> SuccessResponse:
    """Refresh token"""
    tokens = await service.refresh(refresh_token)
    set_tokens_cookie(response, tokens.access_token, tokens.refresh_token)
    return SuccessResponse()

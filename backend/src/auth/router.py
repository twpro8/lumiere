from fastapi import APIRouter, Response, status

from src.auth.dependencies import AuthServiceDep
from src.auth.utils import set_tokens_cookie
from src.core.dependencies import RefreshTokenDep
from src.auth.schemas import (
    UserRegisterSchema,
    UserLoginSchema,
    TokenPair,
)
from src.user.schemas import UserReadSchema

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
) -> UserReadSchema:
    """Register new user"""
    user = await service.create_user(user_data)
    return UserReadSchema.model_validate(user)


@router.post(
    "/login",
    summary="Login user",
)
async def login_user(
    data_login: UserLoginSchema,
    response: Response,
    service: AuthServiceDep,
) -> TokenPair:
    """Login user"""
    tokens = await service.authenticate_user(data_login)
    set_tokens_cookie(response, tokens.access_token, tokens.refresh_token)
    return tokens


@router.post("/refresh", summary="Refresh token")
async def refresh(
    service: AuthServiceDep,
    response: Response,
    refresh_token: RefreshTokenDep,
) -> TokenPair:
    """Refresh token"""
    tokens = await service.refresh(refresh_token)
    set_tokens_cookie(response, tokens.access_token, tokens.refresh_token)
    return tokens

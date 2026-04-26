from fastapi import APIRouter, Response

from src.user.schemas import UserCreateRequestSchema, UserLoginSchema, UserSchema
from src.user.dependencies import UserIdDep, UserServiceDep

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", summary='Register new user')
async def register_user(
        user_data: UserCreateRequestSchema,
        service: UserServiceDep,
) -> dict[str, str]:
    """Register new user"""
    await service.create_user(user_data)
    return {'detail': 'User successfully created!'}


@router.post("/login", summary='Login user')
async def login_user(
        data_login: UserLoginSchema,
        response: Response,
        service: UserServiceDep,
) -> dict[str, str]:
    """Login user"""
    await service.authenticate_user(data_login, response)
    return {'detail': 'User successfully logged in!'}


@router.get("/me", summary='Get current user')
async def current_user(
        user_id: UserIdDep,
        service: UserServiceDep,
) -> UserSchema:
    """Get current user"""
    return await service.get_current_user(user_id)

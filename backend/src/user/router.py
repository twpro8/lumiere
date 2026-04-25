from fastapi import APIRouter, Response

from src.core.dependencies import SessionDep
from src.user.schemas import UserCreateRequestSchema, UserLoginSchema
from src.user.service import UserService
from src.user.dependencies import UserIdDep

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", summary='Register new user')
async def register_user(
        user_data: UserCreateRequestSchema,
        session: SessionDep
) -> dict[str, str]:
    """Register new user"""
    await UserService(session).create_user(user_data)
    return {'detail': 'User successfully created!'}


@router.post("/login", summary='Login user')
async def login_user(
        data_login: UserLoginSchema,
        session: SessionDep,
        response: Response,
):
    """Login user"""
    await UserService(session).authenticate_user(data_login, response)
    return {'detail': 'User successfully logged in!'}


@router.get("/me", summary='Get current user')
async def current_user(user_id: UserIdDep, session: SessionDep):
    """Get current user"""
    return await UserService(session).get_current_user(user_id)

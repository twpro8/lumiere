from uuid import UUID
from typing import Annotated

from fastapi import Request, HTTPException, Depends

from src.auth.security import decode_token

def get_token(request: Request) -> str:
    """get access token"""
    access_token = request.cookies.get('access_token')
    if not access_token:
        raise HTTPException(status_code=401, detail='You have not provided an access token!')
    return access_token

def get_current_user_id(access_token: str = Depends(get_token)) -> int:
    """get current user id from access token"""
    user_id = decode_token(access_token).get('user_id')
    if not user_id:
        raise HTTPException(status_code=401,
                            detail='User ID not found in token!')
    return user_id


UserIdDep = Annotated[UUID, Depends(get_current_user_id)]

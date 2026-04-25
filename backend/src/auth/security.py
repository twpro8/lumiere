from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException
from pwdlib import PasswordHash

from src.core.config import settings

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    """
    Function for generating hashed password
    :param password: user password
    :return: hashed password
    """
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Function for verifying hashed password
    :param plain_password: not hash password
    :param hashed_password: user hash password
    :return: bool
    """
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(token_data: dict) -> str:
    """
    Function for creating access token
    :param token_data: data for token
    :return: access token
    """
    token_data_c = token_data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data_c |= {'expire': expire.isoformat()}
    return jwt.encode(token_data_c, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    """
    Function for decoding token
    :param token: access token
    """
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Не валидный JWT!")

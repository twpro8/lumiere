from src.core.errors.base import AppException


class ChatException(AppException):
    detail = "Chat exception"


class ChatPermissionException(ChatException):
    detail = "User is not member of chat"

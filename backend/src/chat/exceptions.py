from src.core.errors.base import AppException


class ChatException(AppException):
    detail = "Chat exception"


class UserIsNotInChatException(ChatException):
    detail = "User is not in chat"

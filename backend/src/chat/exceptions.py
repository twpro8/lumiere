from src.core.errors.base import AppException


class ChatException(AppException):
    detail = "Chat Exception"


class SelfChatCreationNotAllowed(ChatException):
    detail = "User cannot create a private chat with themselves"

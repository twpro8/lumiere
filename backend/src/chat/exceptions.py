from src.core.errors import AppException


class ChatException(AppException): ...


class MessageException(AppException): ...


class UserIsNotMemberOfChat(MessageException):
    detail = "User is not member of chat"

class DirectChatAlreadyExistException(ChatException):
    detail = "Direct chat already exist between these users"

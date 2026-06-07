from src.core.errors import ObjectNotFoundError, AppException


class ServerError(AppException):
    detail = "Unknown server error"


class ServerNotEmptyError(ServerError):
    detail = "Cannot delete a server that is not empty"


class ServerNotFoundError(ServerError, ObjectNotFoundError):
    detail = "Server not found"


class MemberNotFoundError(ServerError, ObjectNotFoundError):
    detail = "Member not found"

class AppException(Exception):
    detail: str = "Unexpected error"

    def __init__(self, detail: str | None = None) -> None:
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class ObjectNotFoundError(AppException):
    detail = "Object not found"


class ObjectAlreadyExistsError(AppException):
    detail = "Object already exists"

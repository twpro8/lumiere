from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from src.chat.exceptions import ChatException, MessageException

def register_chat_handlers(app: FastAPI):

    @app.exception_handler(ChatException)
    async def chat_exception_handler(request: Request, exc: ChatException):
        return JSONResponse(status_code=400, content={"detail": exc.detail})

    @app.exception_handler(MessageException)
    async def message_exception_handler(request: Request, exc: MessageException):
        return JSONResponse(status_code=403, content={"detail": exc.detail})
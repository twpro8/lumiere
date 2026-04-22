from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from src.core.config import settings
from src.user import router as user_router
from src.core.logging import configure_logging, get_logger
from src.core.redis import init_redis, close_redis
from src.chat.router import router as chat_router
from src.chat.message.router import router as chat_message_router


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # --- Startup ---
    configure_logging()
    logger.info("app.startup", env=settings.APP_ENV)

    # Initialize Redis connection pool
    app.state.redis = await init_redis()

    yield

    # --- Shutdown ---
    logger.info("app.shutdown")

    # Gracefully close Redis connection
    await close_redis(app.state.redis)


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.include_router(user_router)
app.include_router(chat_router)
app.include_router(chat_message_router)

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}

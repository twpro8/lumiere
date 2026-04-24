from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from src.config import settings
from src.user import router as user_router
from src.core.logging import configure_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # startup
    configure_logging()
    logger.info("app.startup", env=settings.APP_ENV)
    yield
    # shutdown
    logger.info("app.shutdown")


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.include_router(user_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}

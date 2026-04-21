from fastapi import FastAPI

from src.user import router as user_router
from src.config import settings

app = FastAPI(title=settings.APP_NAME)
app.include_router(user_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}

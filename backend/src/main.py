from fastapi import FastAPI

from src.user import router as user_router


app = FastAPI()
app.include_router(user_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}

from fastapi import APIRouter


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
async def get_users() -> dict[str, str]:
    return {"message": "List of users"}

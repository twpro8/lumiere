import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.user.models import UserOrm
from src.user.schemas import UserSchema


@pytest.fixture
async def get_all_users(session: AsyncSession) -> list[UserSchema]:
    result = await session.execute(select(UserOrm))
    models = result.scalars().all()
    return [UserSchema.model_validate(model) for model in models]

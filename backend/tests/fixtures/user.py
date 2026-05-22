import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.user.models import UserOrm
from src.user.schemas import UserSchema
from tests.data import users


@pytest.fixture
async def current_user(session: AsyncSession) -> UserSchema:
    user = users[0]
    query = select(UserOrm).filter_by(id=user["id"])
    result = await session.scalars(query)
    return UserSchema.model_validate(result.one())


@pytest.fixture
async def get_all_users(session: AsyncSession) -> list[UserSchema]:
    result = await session.execute(select(UserOrm))
    models = result.scalars().all()
    return [UserSchema.model_validate(model) for model in models]

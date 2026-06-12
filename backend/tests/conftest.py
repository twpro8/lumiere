from typing import AsyncGenerator, Any

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.postgres.engine import null_pool_engine
from src.core.postgres.session import null_pool_session_maker
from src.main import app
from src.core.postgres import Base, get_session
from src.core.models import *  # noqa
from src.user.schemas import UserSchema
from tests.dependency_overrides.redis_client import get_fake_redis_client
from tests.dependency_overrides.session import get_null_pool_session
from tests.seeder import populate_database


@pytest.fixture(scope="session", autouse=True)
def check_test_mode() -> None:
    """Ensure test mode is enabled"""
    assert settings.APP_ENV == "testing"


@pytest.fixture(scope="session", autouse=True)
def override_dependencies(check_test_mode: None) -> None:
    """Override dependencies once for all tests"""
    from src.core.dependencies import get_redis

    app.dependency_overrides[get_session] = get_null_pool_session
    app.dependency_overrides[get_redis] = get_fake_redis_client


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode: None) -> None:
    """Setup database tables"""
    async with null_pool_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session", autouse=True)
async def populated_database(setup_database: None) -> AsyncGenerator[AsyncSession]:
    """Populate database"""
    async with null_pool_session_maker() as session:
        await populate_database(session)
        yield session


@pytest.fixture(name="ac")
async def async_client() -> AsyncGenerator[AsyncClient, Any]:
    """Async client fixture"""
    async with AsyncClient(
        transport=ASGITransport(app),
        base_url="http://test",
    ) as async_client:
        yield async_client


@pytest.fixture
async def authed_client(
    ac: AsyncClient,
    current_user: UserSchema,
) -> AsyncGenerator[AsyncClient, Any]:
    """Authenticated async http client fixture"""
    response = await ac.post(
        "/api/v1/auth/login",
        json={
            "username": current_user.username,
            "password": "12345678",
        },
    )
    assert response.status_code == 200
    assert ac.cookies.get("access_token")
    assert ac.cookies.get("refresh_token")
    yield ac


pytest_plugins = [
    "tests.fixtures.session",
    "tests.fixtures.user",
]

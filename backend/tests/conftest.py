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
from tests.dependency_overrides.session import get_null_pool_session
from tests.seeder import populate_database

data_for_register = {
    "name": "string",
    "username": "string",
    "email": "user@example.com",
    "password": "string",
}

data_for_login = {"username": "string", "password": "string"}


@pytest.fixture(scope="session", autouse=True)
def check_test_mode() -> None:
    """Ensure test mode is enabled"""
    assert settings.APP_ENV == "testing"


@pytest.fixture(scope="session", autouse=True)
def override_dependencies(check_test_mode: None) -> None:
    """Override dependencies once for all tests"""
    app.dependency_overrides[get_session] = get_null_pool_session


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode: None) -> None:
    """Setup database tables"""
    async with null_pool_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(autouse=True)
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


@pytest.fixture(name="ac_auth")
async def ac_auth(ac: AsyncClient) -> AsyncClient:
    await ac.post("/auth/register", json=data_for_register)
    response = await ac.post("/auth/login", json=data_for_login)

    assert response.status_code == 200
    return ac


@pytest.fixture(autouse=True)
async def clean_data(session: AsyncSession) -> AsyncGenerator[Any, None]:
    """Clean database tables"""
    yield
    for table in reversed(Base.metadata.sorted_tables):
        await session.execute(table.delete())
    await session.commit()


pytest_plugins = [
    "tests.fixtures.session",
    "tests.fixtures.user",
    "tests.fixtures.chat",
]

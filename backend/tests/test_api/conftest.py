from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
import httpx
from httpx import ASGITransport

from main import app
from app.core.database import get_db
from app.core.security import get_current_user
from tests.conftest import make_user


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def current_user():
    return make_user(id=1, name="Test User", email="test@test.com")


@pytest.fixture(autouse=True)
def override_deps(mock_db, current_user):
    """Override FastAPI dependencies for all API tests."""
    async def _get_db():
        yield mock_db

    async def _get_current_user():
        return current_user

    app.dependency_overrides[get_db] = _get_db
    app.dependency_overrides[get_current_user] = _get_current_user
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c

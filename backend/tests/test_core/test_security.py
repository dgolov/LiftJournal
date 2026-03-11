"""Tests for app.core.security — password hashing, JWT, get_current_user."""
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from tests.conftest import make_user, scalar_result


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("password", ["secret", "Password123!", "тест"])
def test_hash_password_produces_different_hash_each_time(password):
    h1 = hash_password(password)
    h2 = hash_password(password)
    # bcrypt always generates a unique salt
    assert h1 != h2


def test_hash_password_starts_with_bcrypt_prefix():
    h = hash_password("mypassword")
    assert h.startswith("$2b$")


@pytest.mark.parametrize("password", ["correct", "another", "пароль"])
def test_verify_password_correct(password):
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


@pytest.mark.parametrize("password,wrong", [
    ("correct", "wrong"),
    ("abc", "ABC"),
    ("pass", "pass "),
])
def test_verify_password_wrong(password, wrong):
    hashed = hash_password(password)
    assert verify_password(wrong, hashed) is False


# ---------------------------------------------------------------------------
# JWT token
# ---------------------------------------------------------------------------

def test_create_access_token_contains_user_id():
    from jose import jwt
    from app.config import settings

    token = create_access_token(42)
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    assert payload["sub"] == "42"


def test_create_access_token_custom_expiry():
    from jose import jwt
    from datetime import datetime
    from app.config import settings

    token = create_access_token(1, expires_delta=timedelta(hours=1))
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    exp = datetime.utcfromtimestamp(payload["exp"])
    now = datetime.utcnow()
    # expiry should be roughly 1 hour from now (within 5 seconds tolerance)
    assert abs((exp - now).total_seconds() - 3600) < 5


@pytest.mark.parametrize("user_id", [1, 99, 1000])
def test_create_access_token_parametrized_user_ids(user_id):
    from jose import jwt
    from app.config import settings

    token = create_access_token(user_id)
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    assert payload["sub"] == str(user_id)


# ---------------------------------------------------------------------------
# get_current_user dependency
# ---------------------------------------------------------------------------

async def test_get_current_user_valid_token():
    from app.core.security import get_current_user

    user = make_user(id=7)
    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=scalar_result(user))

    token = create_access_token(7)
    result = await get_current_user(token=token, db=mock_db)
    assert result is user


async def test_get_current_user_invalid_token():
    from app.core.security import get_current_user

    mock_db = AsyncMock()
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token="not.a.valid.token", db=mock_db)
    assert exc_info.value.status_code == 401


async def test_get_current_user_user_not_found():
    from app.core.security import get_current_user

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=scalar_result(None))

    token = create_access_token(999)
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=token, db=mock_db)
    assert exc_info.value.status_code == 401


async def test_get_current_user_expired_token():
    from app.core.security import get_current_user

    mock_db = AsyncMock()
    expired_token = create_access_token(1, expires_delta=timedelta(seconds=-1))
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token=expired_token, db=mock_db)
    assert exc_info.value.status_code == 401

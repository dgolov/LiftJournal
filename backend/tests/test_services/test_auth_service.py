"""Tests for AuthService (register + login)."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.services.auth import AuthService
from tests.conftest import make_user


@pytest.fixture
def mock_db():
    return AsyncMock()


# ---------------------------------------------------------------------------
# register
# ---------------------------------------------------------------------------

async def test_register_success(mock_db):
    user = make_user(id=1, name="Alice", email="alice@test.com")

    with patch("app.services.auth.UserRepository") as MockRepo, \
         patch("app.services.auth.hash_password", return_value="hashed_pw"), \
         patch("app.services.auth.create_access_token", return_value="jwt_token"):

        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_email.return_value = None
        repo.create.return_value = user

        result = await AuthService(mock_db).register("alice@test.com", "pass123", "Alice")

    assert result.access_token == "jwt_token"
    assert result.user_id == 1
    assert result.name == "Alice"
    repo.get_by_email.assert_called_once_with("alice@test.com")
    repo.create.assert_called_once_with(
        email="alice@test.com", hashed_password="hashed_pw", name="Alice"
    )


async def test_register_lowercases_email(mock_db):
    user = make_user(id=2, email="bob@test.com", name="Bob")

    with patch("app.services.auth.UserRepository") as MockRepo, \
         patch("app.services.auth.hash_password", return_value="h"), \
         patch("app.services.auth.create_access_token", return_value="t"):

        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_email.return_value = None
        repo.create.return_value = user

        await AuthService(mock_db).register("BOB@TEST.COM", "pass", "Bob")

    repo.get_by_email.assert_called_once_with("bob@test.com")


async def test_register_email_already_taken(mock_db):
    existing = make_user(id=1, email="taken@test.com")

    with patch("app.services.auth.UserRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_email.return_value = existing

        with pytest.raises(HTTPException) as exc_info:
            await AuthService(mock_db).register("taken@test.com", "pass", "User")

    assert exc_info.value.status_code == 400


# ---------------------------------------------------------------------------
# login
# ---------------------------------------------------------------------------

async def test_login_success(mock_db):
    user = make_user(id=5, name="Eve", hashed_password="real_hash")

    with patch("app.services.auth.UserRepository") as MockRepo, \
         patch("app.services.auth.verify_password", return_value=True), \
         patch("app.services.auth.create_access_token", return_value="tok"):

        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_email.return_value = user

        result = await AuthService(mock_db).login("eve@test.com", "correct")

    assert result.access_token == "tok"
    assert result.user_id == 5


async def test_login_user_not_found(mock_db):
    with patch("app.services.auth.UserRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_email.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await AuthService(mock_db).login("nobody@test.com", "pass")

    assert exc_info.value.status_code == 401


async def test_login_wrong_password(mock_db):
    user = make_user(hashed_password="hash")

    with patch("app.services.auth.UserRepository") as MockRepo, \
         patch("app.services.auth.verify_password", return_value=False):

        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_email.return_value = user

        with pytest.raises(HTTPException) as exc_info:
            await AuthService(mock_db).login("user@test.com", "wrong")

    assert exc_info.value.status_code == 401


async def test_login_user_has_no_password_hash(mock_db):
    user = make_user(hashed_password=None)

    with patch("app.services.auth.UserRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_email.return_value = user

        with pytest.raises(HTTPException) as exc_info:
            await AuthService(mock_db).login("user@test.com", "pass")

    assert exc_info.value.status_code == 401


@pytest.mark.parametrize("email,password", [
    ("a@b.com", ""),
    ("a@b.com", "123"),
    ("A@B.COM", "pass"),
])
async def test_login_lowercases_email(mock_db, email, password):
    with patch("app.services.auth.UserRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_email.return_value = None

        with pytest.raises(HTTPException):
            await AuthService(mock_db).login(email, password)

    repo.get_by_email.assert_called_once_with(email.lower())

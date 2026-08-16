from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.api.schemas import ProfileUpdate, WeightEntryIn, GoalCreate, UserMaxIn, PasswordChange
from app.services.user import UserService
from tests.conftest import make_user, make_weight_entry, make_goal, make_user_max


@pytest.fixture
def mock_db():
    return AsyncMock()


# ---------------------------------------------------------------------------
# get_user
# ---------------------------------------------------------------------------

async def test_get_user_success(mock_db):
    user = make_user(id=1, name="Alex")

    with patch("app.services.user.UserRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_with_relations.return_value = user

        result = await UserService(mock_db).get_user(1)

    assert result.name == "Alex"
    assert result.birthDate is None


async def test_get_user_not_found(mock_db):
    with patch("app.services.user.UserRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_with_relations.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await UserService(mock_db).get_user(999)

    assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# update_profile
# ---------------------------------------------------------------------------

async def test_update_profile_success(mock_db):
    user = make_user(id=1, name="Old Name")
    updated = make_user(id=1, name="New Name")

    with patch("app.services.user.UserRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_with_relations.return_value = user
        repo.update_profile.return_value = updated

        payload = ProfileUpdate(name="New Name")
        result = await UserService(mock_db).update_profile(1, payload)

    assert result.name == "New Name"
    repo.update_profile.assert_called_once_with(
        user, name="New Name", birth_date=None, avatar_url=None
    )


async def test_update_profile_user_not_found(mock_db):
    with patch("app.services.user.UserRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_with_relations.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await UserService(mock_db).update_profile(999, ProfileUpdate())

    assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# log_weight / delete_weight
# ---------------------------------------------------------------------------

async def test_log_weight(mock_db):
    entry = make_weight_entry(date_val=date(2026, 3, 1), kg=79.5)

    with patch("app.services.user.UserRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.upsert_weight.return_value = entry

        payload = WeightEntryIn(date=date(2026, 3, 1), kg=79.5)
        result = await UserService(mock_db).log_weight(1, payload)

    assert result.kg == 79.5
    assert result.date == date(2026, 3, 1)


async def test_delete_weight_valid_date(mock_db):
    with patch("app.services.user.UserRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo

        await UserService(mock_db).delete_weight(1, "2026-03-01")

    repo.delete_weight.assert_called_once_with(1, date(2026, 3, 1))


@pytest.mark.parametrize("bad_date", ["not-a-date", "2026/03/01", "01-03-2026", ""])
async def test_delete_weight_invalid_date(mock_db, bad_date):
    with patch("app.services.user.UserRepository"):
        with pytest.raises(HTTPException) as exc_info:
            await UserService(mock_db).delete_weight(1, bad_date)

    assert exc_info.value.status_code == 422


# ---------------------------------------------------------------------------
# Goals
# ---------------------------------------------------------------------------

async def test_create_goal(mock_db):
    goal = make_goal(id="g-1", text="Run 5k", done=False)

    with patch("app.services.user.UserRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.create_goal.return_value = goal

        payload = GoalCreate(text="Run 5k")
        result = await UserService(mock_db).create_goal(1, payload)

    assert result.id == "g-1"
    assert result.text == "Run 5k"
    assert result.done is False


async def test_toggle_goal_success(mock_db):
    goal = make_goal(id="g-1", done=True)

    with patch("app.services.user.UserRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.toggle_goal.return_value = goal

        result = await UserService(mock_db).toggle_goal(1, "g-1")

    assert result.done is True


async def test_toggle_goal_not_found(mock_db):
    with patch("app.services.user.UserRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.toggle_goal.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await UserService(mock_db).toggle_goal(1, "missing-goal")

    assert exc_info.value.status_code == 404


async def test_delete_goal(mock_db):
    with patch("app.services.user.UserRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo

        await UserService(mock_db).delete_goal(1, "g-1")

    repo.delete_goal.assert_called_once_with(1, "g-1")


# ---------------------------------------------------------------------------
# User maxes
# ---------------------------------------------------------------------------

async def test_upsert_max(mock_db):
    m = make_user_max(exercise_name="Deadlift", weight_kg=180.0)

    with patch("app.services.user.UserRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.upsert_max.return_value = m

        payload = UserMaxIn(exercise_name="Deadlift", weight_kg=180.0)
        result = await UserService(mock_db).upsert_max(1, payload)

    assert result.exercise_name == "Deadlift"
    assert result.weight_kg == 180.0
    repo.upsert_max.assert_called_once_with(1, "Deadlift", 180.0)


async def test_delete_max(mock_db):
    with patch("app.services.user.UserRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo

        await UserService(mock_db).delete_max(1, "Squat")

    repo.delete_max.assert_called_once_with(1, "Squat")


# ---------------------------------------------------------------------------
# change_password
# ---------------------------------------------------------------------------

async def test_change_password_success(mock_db):
    user = make_user(id=1, hashed_password="$2b$12$oldhash")
    payload = PasswordChange(currentPassword="old-pass", newPassword="new-password")

    with patch("app.services.user.UserRepository") as MockRepo, \
         patch("app.services.user.verify_password", return_value=True) as mock_verify, \
         patch("app.services.user.hash_password", return_value="$2b$12$newhash") as mock_hash:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_with_relations.return_value = user

        await UserService(mock_db).change_password(1, payload)

    mock_verify.assert_called_once_with("old-pass", "$2b$12$oldhash")
    mock_hash.assert_called_once_with("new-password")
    repo.update_password.assert_called_once_with(1, "$2b$12$newhash")


async def test_change_password_user_not_found(mock_db):
    payload = PasswordChange(currentPassword="old-pass", newPassword="new-password")

    with patch("app.services.user.UserRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_with_relations.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await UserService(mock_db).change_password(999, payload)

    assert exc_info.value.status_code == 404
    repo.update_password.assert_not_called()


async def test_change_password_wrong_current_password(mock_db):
    user = make_user(id=1, hashed_password="$2b$12$oldhash")
    payload = PasswordChange(currentPassword="wrong-pass", newPassword="new-password")

    with patch("app.services.user.UserRepository") as MockRepo, \
         patch("app.services.user.verify_password", return_value=False):
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_with_relations.return_value = user

        with pytest.raises(HTTPException) as exc_info:
            await UserService(mock_db).change_password(1, payload)

    assert exc_info.value.status_code == 400
    repo.update_password.assert_not_called()


async def test_change_password_no_existing_hash_rejected(mock_db):
    # e.g. an account created via a future OAuth-only flow with no local password set
    user = make_user(id=1, hashed_password=None)
    payload = PasswordChange(currentPassword="anything", newPassword="new-password")

    with patch("app.services.user.UserRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_with_relations.return_value = user

        with pytest.raises(HTTPException) as exc_info:
            await UserService(mock_db).change_password(1, payload)

    assert exc_info.value.status_code == 400
    repo.update_password.assert_not_called()


async def test_change_password_new_password_too_short(mock_db):
    user = make_user(id=1, hashed_password="$2b$12$oldhash")
    payload = PasswordChange(currentPassword="old-pass", newPassword="short")

    with patch("app.services.user.UserRepository") as MockRepo, \
         patch("app.services.user.verify_password", return_value=True):
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_with_relations.return_value = user

        with pytest.raises(HTTPException) as exc_info:
            await UserService(mock_db).change_password(1, payload)

    assert exc_info.value.status_code == 422
    repo.update_password.assert_not_called()


# ---------------------------------------------------------------------------
# _to_dto — mapping correctness
# ---------------------------------------------------------------------------

def test_to_dto_maps_weight_log_sorted():
    from app.services.user import UserService
    from unittest.mock import AsyncMock

    svc = UserService(AsyncMock())
    e1 = make_weight_entry(date_val=date(2026, 3, 5), kg=81.0)
    e2 = make_weight_entry(date_val=date(2026, 1, 1), kg=85.0)
    user = make_user(weight_log=[e1, e2])

    dto = svc._to_dto(user)
    # should be sorted ascending by date
    assert dto.weightLog[0].date == date(2026, 1, 1)
    assert dto.weightLog[1].date == date(2026, 3, 5)


def test_to_dto_maps_maxes():
    from app.services.user import UserService
    from unittest.mock import AsyncMock

    svc = UserService(AsyncMock())
    m = make_user_max(exercise_name="Bench Press", weight_kg=100.0)
    user = make_user(maxes=[m])

    dto = svc._to_dto(user)
    assert len(dto.maxes) == 1
    assert dto.maxes[0].exercise_name == "Bench Press"

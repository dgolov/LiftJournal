"""Tests for UserService."""
from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.api.schemas import ProfileUpdate, WeightEntryIn, GoalCreate, UserMaxIn
from app.services.user import UserService
from tests.conftest import make_user, make_weight_entry, make_goal, make_user_max


@pytest.fixture
def mock_db():
    return AsyncMock()


# ---------------------------------------------------------------------------
# get_user
# ---------------------------------------------------------------------------

async def test_get_user_success(mock_db):
    user = make_user(id=1, name="Alex", age=28)

    with patch("app.services.user.UserRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_with_relations.return_value = user

        result = await UserService(mock_db).get_user(1)

    assert result.name == "Alex"
    assert result.age == 28


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
    updated = make_user(id=1, name="New Name", age=30)

    with patch("app.services.user.UserRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_with_relations.return_value = user
        repo.update_profile.return_value = updated

        payload = ProfileUpdate(name="New Name", age=30)
        result = await UserService(mock_db).update_profile(1, payload)

    assert result.name == "New Name"
    repo.update_profile.assert_called_once_with(
        user, name="New Name", age=30, avatar_url=None
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

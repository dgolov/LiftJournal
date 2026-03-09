from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.api.schemas import WorkoutCreate, WorkoutUpdate
from app.services.workout import WorkoutService
from tests.conftest import make_workout, make_workout_exercise, make_set_orm


@pytest.fixture
def mock_db():
    return AsyncMock()


def _full_workout(user_id=1):
    s = make_set_orm(id="s-1", weight=100.0, reps=5, completed=True)
    we = make_workout_exercise(id="we-1", exercise_id="ex-001", exercise_name="Bench Press", sets=[s])
    return make_workout(id="w-1", user_id=user_id, exercises=[we])


# ---------------------------------------------------------------------------
# get_workouts
# ---------------------------------------------------------------------------

async def test_get_workouts_returns_list(mock_db):
    w = _full_workout()

    with patch("app.services.workout.WorkoutRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_all_by_user.return_value = [w]

        result = await WorkoutService(mock_db).get_workouts(1)

    assert len(result) == 1
    assert result[0].id == "w-1"
    repo.get_all_by_user.assert_called_once_with(1)


async def test_get_workouts_empty(mock_db):
    with patch("app.services.workout.WorkoutRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_all_by_user.return_value = []

        result = await WorkoutService(mock_db).get_workouts(1)

    assert result == []


# ---------------------------------------------------------------------------
# get_workout
# ---------------------------------------------------------------------------

async def test_get_workout_success(mock_db):
    w = _full_workout(user_id=1)

    with patch("app.services.workout.WorkoutRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = w

        result = await WorkoutService(mock_db).get_workout("w-1", 1)

    assert result.id == "w-1"


async def test_get_workout_not_found(mock_db):
    with patch("app.services.workout.WorkoutRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await WorkoutService(mock_db).get_workout("missing", 1)

    assert exc_info.value.status_code == 404


async def test_get_workout_wrong_user_forbidden(mock_db):
    w = _full_workout(user_id=99)

    with patch("app.services.workout.WorkoutRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = w

        with pytest.raises(HTTPException) as exc_info:
            await WorkoutService(mock_db).get_workout("w-1", user_id=1)

    assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# create_workout
# ---------------------------------------------------------------------------

async def test_create_workout(mock_db):
    w = _full_workout()

    with patch("app.services.workout.WorkoutRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.create.return_value = w

        payload = WorkoutCreate(
            date=date(2026, 3, 1), type="Силовая",
            title="Push day", durationMinutes=60,
        )
        result = await WorkoutService(mock_db).create_workout(payload, user_id=1)

    assert result.id == "w-1"
    repo.create.assert_called_once()


# ---------------------------------------------------------------------------
# update_workout
# ---------------------------------------------------------------------------

async def test_update_workout_success(mock_db):
    original = _full_workout(user_id=1)
    updated = make_workout(id="w-1", user_id=1, title="Updated", exercises=[])

    with patch("app.services.workout.WorkoutRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = original
        repo.update.return_value = updated

        payload = WorkoutUpdate(title="Updated")
        result = await WorkoutService(mock_db).update_workout("w-1", payload, user_id=1)

    assert result.title == "Updated"


async def test_update_workout_not_found(mock_db):
    with patch("app.services.workout.WorkoutRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await WorkoutService(mock_db).update_workout("missing", WorkoutUpdate(), 1)

    assert exc_info.value.status_code == 404


async def test_update_workout_wrong_user_forbidden(mock_db):
    w = _full_workout(user_id=99)

    with patch("app.services.workout.WorkoutRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = w

        with pytest.raises(HTTPException) as exc_info:
            await WorkoutService(mock_db).update_workout("w-1", WorkoutUpdate(), user_id=1)

    assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# delete_workout
# ---------------------------------------------------------------------------

async def test_delete_workout_success(mock_db):
    w = _full_workout(user_id=1)

    with patch("app.services.workout.WorkoutRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = w

        await WorkoutService(mock_db).delete_workout("w-1", user_id=1)

    repo.delete.assert_called_once_with(w)


async def test_delete_workout_not_found(mock_db):
    with patch("app.services.workout.WorkoutRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await WorkoutService(mock_db).delete_workout("missing", 1)

    assert exc_info.value.status_code == 404


async def test_delete_workout_wrong_user_forbidden(mock_db):
    w = _full_workout(user_id=99)

    with patch("app.services.workout.WorkoutRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = w

        with pytest.raises(HTTPException) as exc_info:
            await WorkoutService(mock_db).delete_workout("w-1", user_id=1)

    assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# _to_dto — field mapping
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("notes,expected", [
    (None, ""),
    ("", ""),
    ("Some note", "Some note"),
])
def test_to_dto_notes_fallback(notes, expected):
    svc = WorkoutService(AsyncMock())
    w = _full_workout()
    w.notes = notes
    dto = svc._to_dto(w)
    assert dto.notes == expected

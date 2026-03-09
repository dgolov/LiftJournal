"""Tests for WorkoutRepository."""
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.repositories.workout import WorkoutRepository
from tests.conftest import make_workout, make_workout_exercise, make_set_orm, scalar_result, scalars_result


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.delete = AsyncMock()
    return db


@pytest.fixture
def repo(mock_db):
    return WorkoutRepository(mock_db)


def _make_exercise_in():
    s = MagicMock()
    s.weight = 100.0
    s.reps = 5
    s.completed = True
    ex = MagicMock()
    ex.exerciseId = "ex-001"
    ex.exerciseName = "Bench Press"
    ex.sets = [s]
    return ex


# ---------------------------------------------------------------------------
# get_all_by_user
# ---------------------------------------------------------------------------

async def test_get_all_by_user_returns_list(repo, mock_db):
    w1 = make_workout(id="w-1", user_id=1)
    w2 = make_workout(id="w-2", user_id=1)
    mock_db.execute.return_value = scalars_result([w1, w2])

    result = await repo.get_all_by_user(1)

    assert len(result) == 2
    mock_db.execute.assert_called_once()


async def test_get_all_by_user_empty(repo, mock_db):
    mock_db.execute.return_value = scalars_result([])

    result = await repo.get_all_by_user(1)

    assert result == []


# ---------------------------------------------------------------------------
# get_by_id
# ---------------------------------------------------------------------------

async def test_get_by_id_found(repo, mock_db):
    w = make_workout(id="w-1")
    mock_db.execute.return_value = scalar_result(w)

    result = await repo.get_by_id("w-1")

    assert result is w


async def test_get_by_id_not_found(repo, mock_db):
    mock_db.execute.return_value = scalar_result(None)

    result = await repo.get_by_id("missing")

    assert result is None


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------

async def test_create_workout_adds_and_commits(repo, mock_db):
    saved = make_workout(id="w-new")
    # After commit, create() calls get_by_id() which calls db.execute
    mock_db.execute.return_value = scalar_result(saved)

    # Use real ORM classes (no patching) — SQLAlchemy models work without a session
    ex_in = _make_exercise_in()
    await repo.create(
        user_id=1, date=date(2026, 1, 1), type="Силовая",
        title="Push", duration_minutes=60, notes="",
        exercises_data=[ex_in],
    )

    mock_db.add.assert_called()
    mock_db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------

async def test_update_workout_fields(repo, mock_db):
    w = make_workout(id="w-1", title="Old Title")
    updated = make_workout(id="w-1", title="New Title")
    mock_db.execute.return_value = scalar_result(updated)

    result = await repo.update(w, title="New Title")

    assert w.title == "New Title"
    mock_db.commit.assert_called_once()


async def test_update_skips_none_fields(repo, mock_db):
    w = make_workout(id="w-1", title="Keep", notes="Keep notes")
    mock_db.execute.return_value = scalar_result(w)

    await repo.update(w, title=None, notes=None)

    assert w.title == "Keep"
    assert w.notes == "Keep notes"


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------

async def test_delete_workout(repo, mock_db):
    w = make_workout(id="w-1")

    await repo.delete(w)

    mock_db.delete.assert_called_once_with(w)
    mock_db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# _build_exercises
# ---------------------------------------------------------------------------

def test_build_exercises_creates_workout_exercises(repo):
    ex_in = _make_exercise_in()

    with patch("app.repositories.workout.WorkoutExercise") as MockWE, \
         patch("app.repositories.workout.ExerciseSet") as MockSet:

        we = MagicMock()
        we.sets = []
        MockWE.return_value = we
        MockSet.return_value = MagicMock()

        result = repo._build_exercises([ex_in])

    assert len(result) == 1
    MockWE.assert_called_once_with(
        exercise_id="ex-001", exercise_name="Bench Press", order=0
    )


@pytest.mark.parametrize("count", [0, 1, 3, 5])
def test_build_exercises_count(repo, count):
    exercises_in = [_make_exercise_in() for _ in range(count)]

    with patch("app.repositories.workout.WorkoutExercise") as MockWE, \
         patch("app.repositories.workout.ExerciseSet"):

        we = MagicMock()
        we.sets = []
        MockWE.return_value = we

        result = repo._build_exercises(exercises_in)

    assert len(result) == count

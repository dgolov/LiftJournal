from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.repositories.cycle_run import CycleRunRepository
from tests.conftest import (
    make_cycle_run, make_cycle_log, make_cycle_workout,
    make_cycle_exercise, make_cycle_set, scalar_result, scalars_result,
)


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.delete = AsyncMock()
    db.flush = AsyncMock()
    return db


@pytest.fixture
def repo(mock_db):
    return CycleRunRepository(mock_db)


# ---------------------------------------------------------------------------
# get_active_run
# ---------------------------------------------------------------------------

async def test_get_active_run_found(repo, mock_db):
    run = make_cycle_run(id="run-1")
    mock_db.execute.return_value = scalar_result(run)

    result = await repo.get_active_run(user_id=1, cycle_id="cyc-1")

    assert result is run


async def test_get_active_run_not_found(repo, mock_db):
    mock_db.execute.return_value = scalar_result(None)

    result = await repo.get_active_run(user_id=1, cycle_id="cyc-1")

    assert result is None


# ---------------------------------------------------------------------------
# get_run_by_id
# ---------------------------------------------------------------------------

async def test_get_run_by_id_found(repo, mock_db):
    run = make_cycle_run(id="run-1")
    mock_db.execute.return_value = scalar_result(run)

    result = await repo.get_run_by_id("run-1", 1)

    assert result is run


async def test_get_run_by_id_not_found(repo, mock_db):
    mock_db.execute.return_value = scalar_result(None)

    result = await repo.get_run_by_id("missing", 1)

    assert result is None


# ---------------------------------------------------------------------------
# create_run
# ---------------------------------------------------------------------------

async def test_create_run_adds_and_commits(repo, mock_db):
    saved_run = make_cycle_run(id="run-new")
    # After commit, create_run() calls get_run_by_id() which calls db.execute
    mock_db.execute.return_value = scalar_result(saved_run)

    # Use real ORM class (no patching) — SQLAlchemy models work without a session
    result = await repo.create_run(user_id=1, cycle_id="cyc-1")

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# get_cycle_workout
# ---------------------------------------------------------------------------

async def test_get_cycle_workout_found(repo, mock_db):
    cw = make_cycle_workout(id="cw-1")
    mock_db.execute.return_value = scalar_result(cw)

    result = await repo.get_cycle_workout("cw-1")

    assert result is cw


# ---------------------------------------------------------------------------
# get_user_maxes
# ---------------------------------------------------------------------------

async def test_get_user_maxes_returns_dict(repo, mock_db):
    m1 = MagicMock()
    m1.exercise_name = "Bench Press"
    m1.weight_kg = 100.0
    m2 = MagicMock()
    m2.exercise_name = "Squat"
    m2.weight_kg = 150.0

    mock_db.execute.return_value = scalars_result([m1, m2])

    result = await repo.get_user_maxes(1)

    assert result == {"Bench Press": 100.0, "Squat": 150.0}


async def test_get_user_maxes_empty(repo, mock_db):
    mock_db.execute.return_value = scalars_result([])

    result = await repo.get_user_maxes(1)

    assert result == {}


# ---------------------------------------------------------------------------
# create_prefilled_workout — weight calculation
# ---------------------------------------------------------------------------

async def test_create_prefilled_workout_calculates_weight(repo, mock_db):
    """Weight = round(max_kg * percent / 100 / 2.5) * 2.5"""
    cs = make_cycle_set(percent_1rm=80.0, reps=5, order=0)
    ce = make_cycle_exercise(exercise_name="Bench Press", sets=[cs], order=0)
    cw = make_cycle_workout(cycle_id="cyc-1", exercises=[ce])
    run = make_cycle_run(user_id=1, cycle_id="cyc-1", logs=[])

    # After flush, objects need IDs
    saved_workout = MagicMock()
    saved_workout.id = "w-new"
    saved_log = MagicMock()
    saved_log.id = "log-new"

    created_sets = []

    def capture_add(obj):
        pass

    mock_db.add = MagicMock(side_effect=capture_add)

    # Intercept ExerciseSet construction to verify weight
    with patch("app.repositories.cycle_run.Workout") as MockWorkout, \
         patch("app.repositories.cycle_run.WorkoutExercise") as MockWE, \
         patch("app.repositories.cycle_run.ExerciseSet") as MockES, \
         patch("app.repositories.cycle_run.CycleWorkoutLog") as MockLog, \
         patch("app.repositories.cycle_run.gen_uuid", return_value="uuid-1"):

        workout_instance = MagicMock()
        workout_instance.id = "w-new"
        MockWorkout.return_value = workout_instance

        we_instance = MagicMock()
        we_instance.id = "we-new"
        MockWE.return_value = we_instance

        set_instance = MagicMock()
        MockES.return_value = set_instance

        log_instance = MagicMock()
        log_instance.id = "log-new"
        MockLog.return_value = log_instance

        workout, log = await repo.create_prefilled_workout(
            run, cw, "5/3/1", "", {"Bench Press": 100.0}
        )

    # Verify ExerciseSet was created with correct weight: round(100 * 80 / 100 / 2.5) * 2.5 = 80.0
    MockES.assert_called_once()
    call_kwargs = MockES.call_args.kwargs
    assert call_kwargs["weight"] == 80.0
    assert call_kwargs["reps"] == 5
    assert call_kwargs["completed"] is False


async def test_create_prefilled_workout_no_max_uses_zero(repo, mock_db):
    cs = make_cycle_set(percent_1rm=80.0, reps=3, order=0)
    ce = make_cycle_exercise(exercise_name="Deadlift", sets=[cs], order=0)
    cw = make_cycle_workout(cycle_id="cyc-1", exercises=[ce])
    run = make_cycle_run(user_id=1, cycle_id="cyc-1", logs=[])

    with patch("app.repositories.cycle_run.Workout") as MockWorkout, \
         patch("app.repositories.cycle_run.WorkoutExercise") as MockWE, \
         patch("app.repositories.cycle_run.ExerciseSet") as MockES, \
         patch("app.repositories.cycle_run.CycleWorkoutLog"), \
         patch("app.repositories.cycle_run.gen_uuid", return_value="u"):

        MockWorkout.return_value = MagicMock(id="w")
        MockWE.return_value = MagicMock(id="we")
        MockES.return_value = MagicMock()

        await repo.create_prefilled_workout(run, cw, "Prog", "", {})  # no maxes

    call_kwargs = MockES.call_args.kwargs
    assert call_kwargs["weight"] == 0.0  # no max → 0


# ---------------------------------------------------------------------------
# complete_workout_log
# ---------------------------------------------------------------------------

async def test_complete_workout_log_updates_existing_log(repo, mock_db):
    log = make_cycle_log(cycle_workout_id="cw-1", workout_id=None, completed_at=None)
    run = make_cycle_run(id="run-1", logs=[log])
    refreshed_run = make_cycle_run(id="run-1")
    mock_db.execute.return_value = scalar_result(refreshed_run)

    result = await repo.complete_workout_log(run, "cw-1", "w-1")

    assert log.workout_id == "w-1"
    assert log.completed_at is not None
    mock_db.commit.assert_called_once()


async def test_complete_workout_log_creates_new_log_if_missing(repo, mock_db):
    run = make_cycle_run(id="run-1", logs=[])
    refreshed_run = make_cycle_run(id="run-1")
    mock_db.execute.return_value = scalar_result(refreshed_run)

    with patch("app.repositories.cycle_run.CycleWorkoutLog") as MockLog:
        log_instance = MagicMock()
        MockLog.return_value = log_instance

        await repo.complete_workout_log(run, "cw-new", "w-1")

    mock_db.add.assert_called_once_with(log_instance)
    assert log_instance.completed_at is not None


# ---------------------------------------------------------------------------
# finish_run
# ---------------------------------------------------------------------------

async def test_finish_run_sets_completed_at(repo, mock_db):
    run = make_cycle_run(id="run-1", completed_at=None)
    finished = make_cycle_run(id="run-1", completed_at=datetime(2026, 3, 1))
    mock_db.execute.return_value = scalar_result(finished)

    result = await repo.finish_run(run)

    assert run.completed_at is not None
    mock_db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# Weight calculation edge cases
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("max_kg,percent,expected_weight", [
    (100.0, 80.0, 80.0),   # 100 * 80% = 80 → rounded to 80.0
    (100.0, 85.0, 85.0),   # 100 * 85% = 85 → 85.0
    (100.0, 82.5, 82.5),   # 100 * 82.5% = 82.5 → 82.5
    (120.0, 75.0, 90.0),   # 120 * 75% = 90 → 90.0
    (100.0, 77.0, 77.5),   # 100 * 77% = 77 → round to nearest 2.5 = 77.5
])
def test_weight_rounding_formula(max_kg, percent, expected_weight):
    """Verify the rounding formula: round(max * pct / 100 / 2.5) * 2.5"""
    result = round(max_kg * percent / 100 / 2.5) * 2.5
    assert result == expected_weight

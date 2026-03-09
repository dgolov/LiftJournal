from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest


# ---------------------------------------------------------------------------
# DB mock
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.delete = AsyncMock()
    return db


# ---------------------------------------------------------------------------
# SQLAlchemy result helpers
# ---------------------------------------------------------------------------

def scalar_result(value):
    """Mock Result whose .scalar_one_or_none() returns *value*."""
    r = MagicMock()
    r.scalar_one_or_none.return_value = value
    return r


def scalars_result(values: list):
    """Mock Result whose .scalars().all() returns *values*."""
    r = MagicMock()
    scalars = MagicMock()
    scalars.all.return_value = values
    r.scalars.return_value = scalars
    return r


def rows_result(rows: list):
    """Mock Result whose direct iteration yields rows with attributes."""
    r = MagicMock()
    r.__iter__ = MagicMock(return_value=iter(rows))
    return r


# ---------------------------------------------------------------------------
# Model factories — plain MagicMocks shaped like ORM objects
# ---------------------------------------------------------------------------

def make_user(
    id=1, email="user@test.com", name="Test User",
    hashed_password="$2b$12$fakehash",
    age=25, avatar_url=None,
    weight_log=None, goals=None, maxes=None,
):
    u = MagicMock()
    u.id = id
    u.email = email
    u.name = name
    u.hashed_password = hashed_password
    u.age = age
    u.avatar_url = avatar_url
    u.weight_log = weight_log if weight_log is not None else []
    u.goals = goals if goals is not None else []
    u.maxes = maxes if maxes is not None else []
    return u


def make_weight_entry(id=1, user_id=1, date_val=None, kg=80.0):
    e = MagicMock()
    e.id = id
    e.user_id = user_id
    e.date = date_val or date(2026, 1, 1)
    e.kg = kg
    return e


def make_goal(id="goal-1", user_id=1, text="Bench 100 kg", target_date=None, done=False):
    g = MagicMock()
    g.id = id
    g.user_id = user_id
    g.text = text
    g.target_date = target_date
    g.done = done
    return g


def make_user_max(
    id=1, user_id=1, exercise_name="Bench Press",
    weight_kg=100.0, recorded_at=None,
):
    m = MagicMock()
    m.id = id
    m.user_id = user_id
    m.exercise_name = exercise_name
    m.weight_kg = weight_kg
    m.recorded_at = recorded_at or date(2026, 1, 1)
    return m


def make_exercise(
    id="ex-001", name="Bench Press", muscle_group="Грудь",
    secondary_muscles=None, equipment="Штанга",
    description="Классика", is_custom=False,
):
    e = MagicMock()
    e.id = id
    e.name = name
    e.muscle_group = muscle_group
    e.secondary_muscles = secondary_muscles or []
    e.equipment = equipment
    e.description = description
    e.is_custom = is_custom
    return e


def make_set_orm(id="s-1", weight=100.0, reps=5, completed=True, order=0):
    s = MagicMock()
    s.id = id
    s.weight = weight
    s.reps = reps
    s.completed = completed
    s.order = order
    return s


def make_workout_exercise(
    id="we-1", exercise_id="ex-001",
    exercise_name="Bench Press", sets=None, order=0,
):
    we = MagicMock()
    we.id = id
    we.exercise_id = exercise_id
    we.exercise_name = exercise_name
    we.sets = sets if sets is not None else []
    we.order = order
    return we


def make_workout(
    id="w-1", user_id=1, date_val=None, type_="Силовая",
    title="Test Workout", duration_minutes=60,
    notes="", created_at=None, exercises=None,
):
    w = MagicMock()
    w.id = id
    w.user_id = user_id
    w.date = date_val or date(2026, 1, 1)
    w.type = type_
    w.title = title
    w.duration_minutes = duration_minutes
    w.notes = notes
    w.created_at = created_at or datetime(2026, 1, 1, 10, 0)
    w.exercises = exercises if exercises is not None else []
    return w


def make_cycle_set(id="cs-1", percent_1rm=80.0, reps=5, order=0):
    s = MagicMock()
    s.id = id
    s.percent_1rm = percent_1rm
    s.reps = reps
    s.order = order
    return s


def make_cycle_exercise(
    id="ce-1", exercise_id="ex-001",
    exercise_name="Bench Press", sets=None, order=0,
):
    e = MagicMock()
    e.id = id
    e.exercise_id = exercise_id
    e.exercise_name = exercise_name
    e.sets = sets if sets is not None else []
    e.order = order
    return e


def make_cycle_workout(
    id="cw-1", cycle_id="cyc-1", workout_number=1,
    title="День А", notes="", order=0, exercises=None,
):
    w = MagicMock()
    w.id = id
    w.cycle_id = cycle_id
    w.workout_number = workout_number
    w.title = title
    w.notes = notes
    w.order = order
    w.exercises = exercises if exercises is not None else []
    return w


def make_cycle(
    id="cyc-1", created_by=1, title="5/3/1",
    description="Программа Вендлера", author_name="Jim Wendler",
    is_public=True, created_at=None, workouts=None,
):
    c = MagicMock()
    c.id = id
    c.created_by = created_by
    c.title = title
    c.description = description
    c.author_name = author_name
    c.is_public = is_public
    c.created_at = created_at or datetime(2026, 1, 1)
    c.workouts = workouts if workouts is not None else []
    return c


def make_cycle_log(
    id="log-1", run_id="run-1", cycle_workout_id="cw-1",
    workout_id=None, completed_at=None,
):
    log = MagicMock()
    log.id = id
    log.run_id = run_id
    log.cycle_workout_id = cycle_workout_id
    log.workout_id = workout_id
    log.completed_at = completed_at
    return log


def make_cycle_run(
    id="run-1", user_id=1, cycle_id="cyc-1",
    started_at=None, completed_at=None, logs=None,
):
    run = MagicMock()
    run.id = id
    run.user_id = user_id
    run.cycle_id = cycle_id
    run.started_at = started_at or datetime(2026, 1, 1)
    run.completed_at = completed_at
    run.logs = logs if logs is not None else []
    return run

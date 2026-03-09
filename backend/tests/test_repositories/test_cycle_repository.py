"""Tests for CycleRepository."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.repositories.cycle import CycleRepository
from tests.conftest import (
    make_cycle, make_cycle_workout, make_cycle_exercise, make_cycle_set,
    scalar_result, scalars_result,
)


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.delete = AsyncMock()
    return db


@pytest.fixture
def repo(mock_db):
    return CycleRepository(mock_db)


def _workout_in(workout_number=1):
    cs = MagicMock()
    cs.percent_1rm = 80.0
    cs.reps = 5
    ce = MagicMock()
    ce.exercise_id = "ex-001"
    ce.exercise_name = "Bench Press"
    ce.sets = [cs]
    cw = MagicMock()
    cw.workout_number = workout_number
    cw.title = "День А"
    cw.notes = ""
    cw.exercises = [ce]
    return cw


# ---------------------------------------------------------------------------
# get_all_visible
# ---------------------------------------------------------------------------

async def test_get_all_visible_returns_cycles_and_counts(repo, mock_db):
    c = make_cycle(id="cyc-1")
    cycles_result = scalars_result([c])

    count_row = MagicMock()
    count_row.cycle_id = "cyc-1"
    count_row.cnt = 3
    counts_result = MagicMock()
    counts_result.__iter__ = MagicMock(return_value=iter([count_row]))

    mock_db.execute.side_effect = [cycles_result, counts_result]

    cycles, counts = await repo.get_all_visible(user_id=1)

    assert len(cycles) == 1
    assert counts == {"cyc-1": 3}


async def test_get_all_visible_empty(repo, mock_db):
    mock_db.execute.side_effect = [
        scalars_result([]),
        MagicMock(**{"__iter__": MagicMock(return_value=iter([]))}),
    ]

    cycles, counts = await repo.get_all_visible(user_id=1)

    assert cycles == []
    assert counts == {}


# ---------------------------------------------------------------------------
# get_by_id
# ---------------------------------------------------------------------------

async def test_get_by_id_found(repo, mock_db):
    c = make_cycle(id="cyc-1")
    mock_db.execute.return_value = scalar_result(c)

    result = await repo.get_by_id("cyc-1")

    assert result is c


async def test_get_by_id_not_found(repo, mock_db):
    mock_db.execute.return_value = scalar_result(None)

    result = await repo.get_by_id("missing")

    assert result is None


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------

async def test_create_cycle_adds_and_commits(repo, mock_db):
    saved = make_cycle(id="cyc-new")
    # After commit, create() calls get_by_id() which calls db.execute
    mock_db.execute.return_value = scalar_result(saved)

    # Use real ORM classes (no patching) — SQLAlchemy models work without a session
    await repo.create(
        created_by=1, title="5/3/1", description="",
        author_name="", is_public=True,
        workouts_data=[_workout_in()],
    )

    mock_db.add.assert_called()
    mock_db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------

async def test_update_cycle_title(repo, mock_db):
    c = make_cycle(id="cyc-1", title="Old")
    updated = make_cycle(id="cyc-1", title="New")
    mock_db.execute.return_value = scalar_result(updated)

    await repo.update(c, title="New")

    assert c.title == "New"
    mock_db.commit.assert_called_once()


async def test_update_skips_none_fields(repo, mock_db):
    c = make_cycle(id="cyc-1", title="Keep", is_public=True)
    mock_db.execute.return_value = scalar_result(c)

    await repo.update(c, title=None, is_public=None)

    assert c.title == "Keep"
    assert c.is_public is True


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------

async def test_delete_cycle(repo, mock_db):
    c = make_cycle()

    await repo.delete(c)

    mock_db.delete.assert_called_once_with(c)
    mock_db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# _build_workouts
# ---------------------------------------------------------------------------

def test_build_workouts_creates_hierarchy(repo):
    w_in = _workout_in(workout_number=1)

    with patch("app.repositories.cycle.CycleWorkout") as MockCW, \
         patch("app.repositories.cycle.CycleExercise") as MockCE, \
         patch("app.repositories.cycle.CycleSet") as MockCS:

        cw = MagicMock()
        cw.exercises = []
        MockCW.return_value = cw

        ce = MagicMock()
        ce.sets = []
        MockCE.return_value = ce

        MockCS.return_value = MagicMock()

        result = repo._build_workouts([w_in])

    assert len(result) == 1
    MockCW.assert_called_once_with(workout_number=1, title="День А", notes="", order=0)


@pytest.mark.parametrize("count", [0, 1, 4])
def test_build_workouts_count(repo, count):
    workouts_in = [_workout_in(i + 1) for i in range(count)]

    with patch("app.repositories.cycle.CycleWorkout") as MockCW, \
         patch("app.repositories.cycle.CycleExercise"), \
         patch("app.repositories.cycle.CycleSet"):

        cw = MagicMock()
        cw.exercises = []
        MockCW.return_value = cw

        result = repo._build_workouts(workouts_in)

    assert len(result) == count


def test_build_workouts_none_input(repo):
    result = repo._build_workouts(None)
    assert result == []

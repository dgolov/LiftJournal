from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.services.cycle_run import CycleRunService
from tests.conftest import make_cycle, make_cycle_run, make_cycle_log, make_cycle_workout


@pytest.fixture
def mock_db():
    return AsyncMock()


def _run_with_log(completed=False):
    log = make_cycle_log(
        id="log-1", cycle_workout_id="cw-1",
        workout_id="w-1",
        completed_at=datetime(2026, 1, 1) if completed else None,
    )
    return make_cycle_run(id="run-1", user_id=1, cycle_id="cyc-1", logs=[log])


# ---------------------------------------------------------------------------
# get_active_run
# ---------------------------------------------------------------------------

async def test_get_active_run_returns_dto(mock_db):
    run = make_cycle_run(id="run-1")

    with patch("app.services.cycle_run.CycleRunRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_active_run.return_value = run

        result = await CycleRunService(mock_db).get_active_run("cyc-1", user_id=1)

    assert result is not None
    assert result.id == "run-1"
    repo.get_active_run.assert_called_once_with(1, "cyc-1")


async def test_get_active_run_returns_none_when_not_started(mock_db):
    with patch("app.services.cycle_run.CycleRunRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_active_run.return_value = None

        result = await CycleRunService(mock_db).get_active_run("cyc-1", user_id=1)

    assert result is None


# ---------------------------------------------------------------------------
# start_run
# ---------------------------------------------------------------------------

async def test_start_run_returns_existing_run_if_active(mock_db):
    run = make_cycle_run(id="run-existing")

    with patch("app.services.cycle_run.CycleRunRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_active_run.return_value = run

        result = await CycleRunService(mock_db).start_run("cyc-1", user_id=1)

    assert result.id == "run-existing"
    repo.create_run.assert_not_called()


async def test_start_run_cycle_not_found(mock_db):
    with patch("app.services.cycle_run.CycleRunRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_active_run.return_value = None
        repo.get_cycle.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await CycleRunService(mock_db).start_run("missing", user_id=1)

    assert exc_info.value.status_code == 404


async def test_start_run_private_cycle_forbidden(mock_db):
    cycle = make_cycle(id="cyc-1", created_by=99, is_public=False)

    with patch("app.services.cycle_run.CycleRunRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_active_run.return_value = None
        repo.get_cycle.return_value = cycle

        with pytest.raises(HTTPException) as exc_info:
            await CycleRunService(mock_db).start_run("cyc-1", user_id=1)

    assert exc_info.value.status_code == 403


async def test_start_run_creates_new_run(mock_db):
    cycle = make_cycle(id="cyc-1", is_public=True)
    new_run = make_cycle_run(id="run-new")

    with patch("app.services.cycle_run.CycleRunRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_active_run.return_value = None
        repo.get_cycle.return_value = cycle
        repo.create_run.return_value = new_run

        result = await CycleRunService(mock_db).start_run("cyc-1", user_id=1)

    assert result.id == "run-new"
    repo.create_run.assert_called_once_with(1, "cyc-1")


# ---------------------------------------------------------------------------
# start_workout
# ---------------------------------------------------------------------------

async def test_start_workout_run_not_found(mock_db):
    with patch("app.services.cycle_run.CycleRunRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_run_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await CycleRunService(mock_db).start_workout("run-1", "cw-1", "", 1)

    assert exc_info.value.status_code == 404


async def test_start_workout_already_started_returns_existing(mock_db):
    log = make_cycle_log(cycle_workout_id="cw-1", workout_id="w-existing")
    run = make_cycle_run(id="run-1", logs=[log])

    with patch("app.services.cycle_run.CycleRunRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_run_by_id.return_value = run

        result = await CycleRunService(mock_db).start_workout("run-1", "cw-1", "", 1)

    assert result["workout_id"] == "w-existing"
    repo.create_prefilled_workout.assert_not_called()


async def test_start_workout_cycle_workout_not_found(mock_db):
    run = make_cycle_run(id="run-1", cycle_id="cyc-1", logs=[])

    with patch("app.services.cycle_run.CycleRunRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_run_by_id.return_value = run
        repo.get_cycle_workout.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await CycleRunService(mock_db).start_workout("run-1", "cw-missing", "", 1)

    assert exc_info.value.status_code == 404


async def test_start_workout_wrong_cycle(mock_db):
    run = make_cycle_run(id="run-1", cycle_id="cyc-1", logs=[])
    cw = make_cycle_workout(id="cw-1", cycle_id="cyc-OTHER")

    with patch("app.services.cycle_run.CycleRunRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_run_by_id.return_value = run
        repo.get_cycle_workout.return_value = cw

        with pytest.raises(HTTPException) as exc_info:
            await CycleRunService(mock_db).start_workout("run-1", "cw-1", "", 1)

    assert exc_info.value.status_code == 404


async def test_start_workout_creates_prefilled_workout(mock_db):
    run = make_cycle_run(id="run-1", cycle_id="cyc-1", logs=[])
    cw = make_cycle_workout(id="cw-1", cycle_id="cyc-1")
    cycle = make_cycle(id="cyc-1", title="5/3/1")

    created_workout = MagicMock()
    created_workout.id = "w-new"
    created_log = MagicMock()
    created_log.id = "log-new"

    with patch("app.services.cycle_run.CycleRunRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_run_by_id.return_value = run
        repo.get_cycle_workout.return_value = cw
        repo.get_cycle.return_value = cycle
        repo.get_user_maxes.return_value = {"Bench Press": 100.0}
        repo.create_prefilled_workout.return_value = (created_workout, created_log)

        result = await CycleRunService(mock_db).start_workout("run-1", "cw-1", "notes", 1)

    assert result["workout_id"] == "w-new"
    assert result["run_id"] == "run-1"
    repo.create_prefilled_workout.assert_called_once()


# ---------------------------------------------------------------------------
# complete_workout
# ---------------------------------------------------------------------------

async def test_complete_workout_run_not_found(mock_db):
    with patch("app.services.cycle_run.CycleRunRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_run_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await CycleRunService(mock_db).complete_workout("run-1", "cw-1", None, 1)

    assert exc_info.value.status_code == 404


async def test_complete_workout_success(mock_db):
    run = make_cycle_run(id="run-1")
    updated_run = make_cycle_run(id="run-1")

    with patch("app.services.cycle_run.CycleRunRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_run_by_id.return_value = run
        repo.complete_workout_log.return_value = updated_run

        result = await CycleRunService(mock_db).complete_workout("run-1", "cw-1", "w-1", 1)

    assert result.id == "run-1"
    repo.complete_workout_log.assert_called_once_with(run, "cw-1", "w-1")


# ---------------------------------------------------------------------------
# finish_run
# ---------------------------------------------------------------------------

async def test_finish_run_not_found(mock_db):
    with patch("app.services.cycle_run.CycleRunRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_run_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await CycleRunService(mock_db).finish_run("run-1", user_id=1)

    assert exc_info.value.status_code == 404


async def test_finish_run_success(mock_db):
    run = make_cycle_run(id="run-1")
    finished = make_cycle_run(id="run-1", completed_at=datetime(2026, 3, 1))

    with patch("app.services.cycle_run.CycleRunRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_run_by_id.return_value = run
        repo.finish_run.return_value = finished

        result = await CycleRunService(mock_db).finish_run("run-1", user_id=1)

    assert result.completed_at is not None
    repo.finish_run.assert_called_once_with(run)

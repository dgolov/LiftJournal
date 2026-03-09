from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.api.schemas import CycleCreate, CycleUpdate
from app.services.cycle import CycleService
from tests.conftest import make_cycle, make_cycle_workout, make_cycle_exercise, make_cycle_set


@pytest.fixture
def mock_db():
    return AsyncMock()


def _cycle_with_workouts(created_by=1, is_public=True):
    cs = make_cycle_set(id="cs-1", percent_1rm=80.0, reps=5, order=0)
    ce = make_cycle_exercise(id="ce-1", exercise_id="ex-001", exercise_name="Bench Press", sets=[cs])
    cw = make_cycle_workout(id="cw-1", cycle_id="cyc-1", workout_number=1, exercises=[ce])
    return make_cycle(id="cyc-1", created_by=created_by, is_public=is_public, workouts=[cw])


# ---------------------------------------------------------------------------
# list_cycles
# ---------------------------------------------------------------------------

async def test_list_cycles_returns_list(mock_db):
    c = make_cycle(id="cyc-1", title="5/3/1")

    with patch("app.services.cycle.CycleRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_all_visible.return_value = ([c], {"cyc-1": 3})

        result = await CycleService(mock_db).list_cycles(user_id=1)

    assert len(result) == 1
    assert result[0].id == "cyc-1"
    assert result[0].workout_count == 3


async def test_list_cycles_empty(mock_db):
    with patch("app.services.cycle.CycleRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_all_visible.return_value = ([], {})

        result = await CycleService(mock_db).list_cycles(user_id=1)

    assert result == []


# ---------------------------------------------------------------------------
# get_cycle
# ---------------------------------------------------------------------------

async def test_get_cycle_public_success(mock_db):
    c = _cycle_with_workouts(created_by=99, is_public=True)

    with patch("app.services.cycle.CycleRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = c

        result = await CycleService(mock_db).get_cycle("cyc-1", user_id=1)

    assert result.id == "cyc-1"


async def test_get_cycle_private_by_owner(mock_db):
    c = _cycle_with_workouts(created_by=1, is_public=False)

    with patch("app.services.cycle.CycleRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = c

        result = await CycleService(mock_db).get_cycle("cyc-1", user_id=1)

    assert result.id == "cyc-1"


async def test_get_cycle_private_other_user_forbidden(mock_db):
    c = _cycle_with_workouts(created_by=99, is_public=False)

    with patch("app.services.cycle.CycleRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = c

        with pytest.raises(HTTPException) as exc_info:
            await CycleService(mock_db).get_cycle("cyc-1", user_id=1)

    assert exc_info.value.status_code == 403


async def test_get_cycle_not_found(mock_db):
    with patch("app.services.cycle.CycleRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await CycleService(mock_db).get_cycle("missing", user_id=1)

    assert exc_info.value.status_code == 404


# ---------------------------------------------------------------------------
# create_cycle
# ---------------------------------------------------------------------------

async def test_create_cycle(mock_db):
    c = _cycle_with_workouts()

    with patch("app.services.cycle.CycleRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.create.return_value = c

        payload = CycleCreate(title="5/3/1", description="", is_public=True)
        result = await CycleService(mock_db).create_cycle(payload, user_id=1)

    assert result.id == "cyc-1"
    repo.create.assert_called_once_with(
        created_by=1,
        title="5/3/1",
        description="",
        author_name="",
        is_public=True,
        workouts_data=[],
    )


# ---------------------------------------------------------------------------
# update_cycle
# ---------------------------------------------------------------------------

async def test_update_cycle_success(mock_db):
    original = _cycle_with_workouts(created_by=1)
    updated = _cycle_with_workouts(created_by=1)
    updated.title = "Updated title"

    with patch("app.services.cycle.CycleRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = original
        repo.update.return_value = updated

        payload = CycleUpdate(title="Updated title")
        result = await CycleService(mock_db).update_cycle("cyc-1", payload, user_id=1)

    assert result.title == "Updated title"


async def test_update_cycle_not_found(mock_db):
    with patch("app.services.cycle.CycleRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await CycleService(mock_db).update_cycle("missing", CycleUpdate(), user_id=1)

    assert exc_info.value.status_code == 404


async def test_update_cycle_wrong_user_forbidden(mock_db):
    c = _cycle_with_workouts(created_by=99)

    with patch("app.services.cycle.CycleRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = c

        with pytest.raises(HTTPException) as exc_info:
            await CycleService(mock_db).update_cycle("cyc-1", CycleUpdate(), user_id=1)

    assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# delete_cycle
# ---------------------------------------------------------------------------

async def test_delete_cycle_success(mock_db):
    c = _cycle_with_workouts(created_by=1)

    with patch("app.services.cycle.CycleRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = c

        await CycleService(mock_db).delete_cycle("cyc-1", user_id=1)

    repo.delete.assert_called_once_with(c)


async def test_delete_cycle_not_found(mock_db):
    with patch("app.services.cycle.CycleRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await CycleService(mock_db).delete_cycle("missing", user_id=1)

    assert exc_info.value.status_code == 404


async def test_delete_cycle_wrong_user_forbidden(mock_db):
    c = _cycle_with_workouts(created_by=99)

    with patch("app.services.cycle.CycleRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = c

        with pytest.raises(HTTPException) as exc_info:
            await CycleService(mock_db).delete_cycle("cyc-1", user_id=1)

    assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# _to_detail — DTO field mapping
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("description,author_name", [
    (None, None),
    ("", ""),
    ("Desc", "Author"),
])
def test_to_detail_null_fallbacks(description, author_name):
    svc = CycleService(AsyncMock())
    c = _cycle_with_workouts()
    c.description = description
    c.author_name = author_name
    dto = svc._to_detail(c)
    assert dto.description == (description or "")
    assert dto.author_name == (author_name or "")

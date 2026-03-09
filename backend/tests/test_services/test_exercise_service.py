"""Tests for ExerciseService."""
from unittest.mock import AsyncMock, patch

import pytest

from app.api.schemas import ExerciseCreate
from app.services.exercise import ExerciseService
from tests.conftest import make_exercise


@pytest.fixture
def mock_db():
    return AsyncMock()


# ---------------------------------------------------------------------------
# list_exercises
# ---------------------------------------------------------------------------

async def test_list_exercises_returns_empty_list(mock_db):
    with patch("app.services.exercise.ExerciseRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_all.return_value = []

        result = await ExerciseService(mock_db).list_exercises()

    assert result == []


async def test_list_exercises_returns_dtos(mock_db):
    ex1 = make_exercise(id="ex-001", name="Bench Press", muscle_group="Грудь")
    ex2 = make_exercise(id="ex-002", name="Squat", muscle_group="Квадрицепсы")

    with patch("app.services.exercise.ExerciseRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_all.return_value = [ex1, ex2]

        result = await ExerciseService(mock_db).list_exercises()

    assert len(result) == 2
    assert result[0].id == "ex-001"
    assert result[0].name == "Bench Press"
    assert result[0].muscleGroup == "Грудь"
    assert result[1].id == "ex-002"


# ---------------------------------------------------------------------------
# create_custom
# ---------------------------------------------------------------------------

async def test_create_custom_returns_dto(mock_db):
    saved = make_exercise(
        id="ex-new", name="Cable Fly", muscle_group="Грудь",
        equipment="Кабель", is_custom=True,
    )

    with patch("app.services.exercise.ExerciseRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.create.return_value = saved

        payload = ExerciseCreate(
            name="Cable Fly", muscleGroup="Грудь",
            equipment="Кабель", description="",
        )
        result = await ExerciseService(mock_db).create_custom(payload)

    assert result.id == "ex-new"
    assert result.isCustom is True
    repo.create.assert_called_once_with(
        name="Cable Fly",
        muscle_group="Грудь",
        secondary_muscles=[],
        equipment="Кабель",
        description="",
    )


# ---------------------------------------------------------------------------
# _to_dto — field mapping
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("secondary_muscles,expected", [
    (None, []),
    ([], []),
    (["Трицепс"], ["Трицепс"]),
    (["Трицепс", "Дельты"], ["Трицепс", "Дельты"]),
])
def test_to_dto_secondary_muscles(secondary_muscles, expected):
    svc = ExerciseService(AsyncMock())
    ex = make_exercise(secondary_muscles=secondary_muscles)
    dto = svc._to_dto(ex)
    assert dto.secondaryMuscles == expected


@pytest.mark.parametrize("description,expected", [
    (None, ""),
    ("", ""),
    ("Some desc", "Some desc"),
])
def test_to_dto_description_fallback(description, expected):
    svc = ExerciseService(AsyncMock())
    ex = make_exercise(description=description)
    dto = svc._to_dto(ex)
    assert dto.description == expected

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.repositories.exercise import ExerciseRepository
from tests.conftest import make_exercise, scalars_result


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    return db


@pytest.fixture
def repo(mock_db):
    return ExerciseRepository(mock_db)


# ---------------------------------------------------------------------------
# get_all
# ---------------------------------------------------------------------------

async def test_get_all_returns_list(repo, mock_db):
    ex1 = make_exercise(id="ex-001", name="Bench Press")
    ex2 = make_exercise(id="ex-002", name="Squat")
    mock_db.execute.return_value = scalars_result([ex1, ex2])

    result = await repo.get_all()

    assert len(result) == 2
    assert result[0].name == "Bench Press"
    mock_db.execute.assert_called_once()


async def test_get_all_empty(repo, mock_db):
    mock_db.execute.return_value = scalars_result([])

    result = await repo.get_all()

    assert result == []


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------

async def test_create_sets_is_custom_true(repo, mock_db):
    mock_db.refresh = AsyncMock()

    with patch("app.repositories.exercise.Exercise") as MockExercise:
        instance = MagicMock()
        MockExercise.return_value = instance

        await repo.create(
            name="Cable Fly",
            muscle_group="Грудь",
            secondary_muscles=[],
            equipment="Кабель",
            description="",
        )

    MockExercise.assert_called_once_with(
        name="Cable Fly",
        muscle_group="Грудь",
        secondary_muscles=[],
        equipment="Кабель",
        description="",
        is_custom=True,
    )
    mock_db.add.assert_called_once_with(instance)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(instance)


@pytest.mark.parametrize("name,muscle_group,equipment", [
    ("Push-up", "Грудь", "Без оборудования"),
    ("Pull-up", "Спина", "Турник"),
    ("Leg Press", "Квадрицепсы", "Тренажёр"),
])
async def test_create_parametrized_exercises(repo, mock_db, name, muscle_group, equipment):
    mock_db.refresh = AsyncMock()

    with patch("app.repositories.exercise.Exercise") as MockExercise:
        instance = MagicMock()
        MockExercise.return_value = instance

        await repo.create(
            name=name,
            muscle_group=muscle_group,
            secondary_muscles=[],
            equipment=equipment,
            description="",
        )

    assert MockExercise.call_args.kwargs["name"] == name
    assert MockExercise.call_args.kwargs["muscle_group"] == muscle_group
    assert MockExercise.call_args.kwargs["is_custom"] is True

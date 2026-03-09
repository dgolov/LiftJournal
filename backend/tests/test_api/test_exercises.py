from unittest.mock import AsyncMock, patch

import pytest

from app.api.schemas import ExerciseOut


def _ex_out(id="ex-001", name="Bench Press"):
    return ExerciseOut(
        id=id, name=name, muscleGroup="Грудь",
        secondaryMuscles=[], equipment="Штанга",
        description="", isCustom=False,
    )


async def test_list_exercises_empty(client):
    with patch("app.api.routers.exercises.ExerciseService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.list_exercises.return_value = []

        resp = await client.get("/api/exercises")

    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_exercises_returns_list(client):
    exercises = [
        _ex_out("ex-001", "Bench Press"),
        _ex_out("ex-002", "Squat")
    ]

    with patch("app.api.routers.exercises.ExerciseService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.list_exercises.return_value = exercises

        resp = await client.get("/api/exercises")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["name"] == "Bench Press"
    assert data[1]["name"] == "Squat"


async def test_create_custom_exercise(client):
    created = ExerciseOut(
        id="ex-new", name="Cable Fly", muscleGroup="Грудь",
        secondaryMuscles=[], equipment="Кабель",
        description="", isCustom=True,
    )

    with patch("app.api.routers.exercises.ExerciseService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.create_custom.return_value = created

        resp = await client.post("/api/exercises", json={
            "name": "Cable Fly", "muscleGroup": "Грудь",
            "equipment": "Кабель",
        })

    assert resp.status_code == 201
    data = resp.json()
    assert data["id"] == "ex-new"
    assert data["isCustom"] is True


async def test_create_exercise_missing_required_fields_returns_422(client):
    resp = await client.post("/api/exercises", json={"name": "Fly"})
    assert resp.status_code == 422


@pytest.mark.parametrize("name,muscle_group,equipment", [
    ("Push-up", "Грудь", "Без оборудования"),
    ("Chin-up", "Спина", "Турник"),
])
async def test_create_exercise_parametrized(client, name, muscle_group, equipment):
    created = ExerciseOut(
        id="ex-x", name=name, muscleGroup=muscle_group,
        secondaryMuscles=[], equipment=equipment,
        description="", isCustom=True,
    )

    with patch("app.api.routers.exercises.ExerciseService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.create_custom.return_value = created

        resp = await client.post("/api/exercises", json={
            "name": name, "muscleGroup": muscle_group, "equipment": equipment
        })

    assert resp.status_code == 201
    assert resp.json()["name"] == name

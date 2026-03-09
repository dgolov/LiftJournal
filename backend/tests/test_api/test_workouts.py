from datetime import date, datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.api.schemas import WorkoutOut


def _workout_out(id="w-1"):
    return WorkoutOut(
        id=id, date=date(2026, 1, 1), type="Силовая",
        title="Test Workout", durationMinutes=60,
        notes="", createdAt=datetime(2026, 1, 1), exercises=[],
    )


async def test_list_workouts(client):
    workouts = [_workout_out("w-1"), _workout_out("w-2")]

    with patch("app.api.routers.workouts.WorkoutService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_workouts.return_value = workouts

        resp = await client.get("/api/workouts")

    assert resp.status_code == 200
    assert len(resp.json()) == 2
    svc.get_workouts.assert_called_once_with(1)


async def test_list_workouts_empty(client):
    with patch("app.api.routers.workouts.WorkoutService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_workouts.return_value = []

        resp = await client.get("/api/workouts")

    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_workout(client):
    with patch("app.api.routers.workouts.WorkoutService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.create_workout.return_value = _workout_out()

        resp = await client.post("/api/workouts", json={
            "date": "2026-01-01", "type": "Силовая",
            "title": "Test Workout", "durationMinutes": 60,
        })

    assert resp.status_code == 201
    assert resp.json()["id"] == "w-1"


async def test_create_workout_missing_required_fields_returns_422(client):
    resp = await client.post("/api/workouts", json={"title": "Test"})
    assert resp.status_code == 422


async def test_get_workout(client):
    with patch("app.api.routers.workouts.WorkoutService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_workout.return_value = _workout_out()

        resp = await client.get("/api/workouts/w-1")

    assert resp.status_code == 200
    svc.get_workout.assert_called_once_with("w-1", 1)


async def test_get_workout_not_found(client):
    with patch("app.api.routers.workouts.WorkoutService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_workout.side_effect = HTTPException(status_code=404)

        resp = await client.get("/api/workouts/missing")

    assert resp.status_code == 404


async def test_get_workout_forbidden(client):
    with patch("app.api.routers.workouts.WorkoutService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_workout.side_effect = HTTPException(status_code=403)

        resp = await client.get("/api/workouts/w-other")

    assert resp.status_code == 403


async def test_update_workout(client):
    with patch("app.api.routers.workouts.WorkoutService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.update_workout.return_value = _workout_out()

        resp = await client.patch("/api/workouts/w-1", json={"title": "Updated"})

    assert resp.status_code == 200
    svc.update_workout.assert_called_once()


async def test_delete_workout(client):
    with patch("app.api.routers.workouts.WorkoutService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc

        resp = await client.delete("/api/workouts/w-1")

    assert resp.status_code == 204
    svc.delete_workout.assert_called_once_with("w-1", 1)


async def test_delete_workout_not_found(client):
    with patch("app.api.routers.workouts.WorkoutService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.delete_workout.side_effect = HTTPException(status_code=404)

        resp = await client.delete("/api/workouts/missing")

    assert resp.status_code == 404


@pytest.mark.parametrize("workout_type", ["Силовая", "Кардио", "HIIT", "Растяжка"])
async def test_create_workout_various_types(client, workout_type):
    out = WorkoutOut(
        id="w-new", date=date(2026, 1, 1), type=workout_type,
        title="Workout", durationMinutes=30,
        notes="", createdAt=datetime(2026, 1, 1), exercises=[],
    )

    with patch("app.api.routers.workouts.WorkoutService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.create_workout.return_value = out

        resp = await client.post("/api/workouts", json={
            "date": "2026-01-01", "type": workout_type, "title": "Workout"
        })

    assert resp.status_code == 201
    assert resp.json()["type"] == workout_type

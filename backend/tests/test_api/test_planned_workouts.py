from datetime import date, datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.api.schemas import PlannedWorkoutOut


def _plan(id="plan-1", status="planned"):
    return PlannedWorkoutOut(
        id=id, title="Силовая тренировка", type="Силовая",
        scheduledDate=date(2026, 6, 1), notes="",
        status=status, completedWorkoutId=None,
        createdAt=datetime(2026, 1, 1), exercises=[],
    )


async def test_list_planned(client):
    plans = [_plan("plan-1"), _plan("plan-2")]

    with patch("app.api.routers.planned_workouts.PlannedWorkoutService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_all.return_value = plans

        resp = await client.get("/api/planned-workouts")

    assert resp.status_code == 200
    assert len(resp.json()) == 2
    svc.get_all.assert_called_once_with(1)


async def test_list_planned_empty(client):
    with patch("app.api.routers.planned_workouts.PlannedWorkoutService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_all.return_value = []

        resp = await client.get("/api/planned-workouts")

    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_planned(client):
    with patch("app.api.routers.planned_workouts.PlannedWorkoutService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.create.return_value = _plan()

        resp = await client.post("/api/planned-workouts", json={
            "title": "Силовая тренировка",
            "type": "Силовая",
            "scheduledDate": "2026-06-01",
        })

    assert resp.status_code == 201
    assert resp.json()["id"] == "plan-1"
    svc.create.assert_called_once()


async def test_create_planned_missing_required_returns_422(client):
    resp = await client.post("/api/planned-workouts", json={"title": "test"})
    assert resp.status_code == 422


async def test_update_planned(client):
    with patch("app.api.routers.planned_workouts.PlannedWorkoutService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.update.return_value = _plan(status="completed")

        resp = await client.patch("/api/planned-workouts/plan-1", json={"status": "completed"})

    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"
    svc.update.assert_called_once()


async def test_update_planned_not_found(client):
    with patch("app.api.routers.planned_workouts.PlannedWorkoutService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.update.side_effect = HTTPException(status_code=404, detail="Planned workout not found")

        resp = await client.patch("/api/planned-workouts/missing", json={"title": "x"})

    assert resp.status_code == 404


async def test_delete_planned(client):
    with patch("app.api.routers.planned_workouts.PlannedWorkoutService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.delete.return_value = None

        resp = await client.delete("/api/planned-workouts/plan-1")

    assert resp.status_code == 204
    svc.delete.assert_called_once_with("plan-1", 1)


async def test_delete_planned_not_found(client):
    with patch("app.api.routers.planned_workouts.PlannedWorkoutService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.delete.side_effect = HTTPException(status_code=404, detail="Planned workout not found")

        resp = await client.delete("/api/planned-workouts/missing")

    assert resp.status_code == 404

"""Tests for cycle run endpoints (/api/cycles/.../run, /api/cycle-runs/...)."""
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.api.schemas import CycleRunOut


def _run_out(id="run-1", completed_at=None):
    return CycleRunOut(
        id=id, cycle_id="cyc-1",
        started_at=datetime(2026, 1, 1),
        completed_at=completed_at,
        logs=[],
    )


async def test_get_active_run_found(client):
    with patch("app.api.routers.cycle_runs.CycleRunService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_active_run.return_value = _run_out()

        resp = await client.get("/api/cycles/cyc-1/run")

    assert resp.status_code == 200
    assert resp.json()["id"] == "run-1"
    svc.get_active_run.assert_called_once_with("cyc-1", 1)


async def test_get_active_run_not_started_returns_null(client):
    with patch("app.api.routers.cycle_runs.CycleRunService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_active_run.return_value = None

        resp = await client.get("/api/cycles/cyc-1/run")

    assert resp.status_code == 200
    assert resp.json() is None


async def test_start_cycle_run(client):
    with patch("app.api.routers.cycle_runs.CycleRunService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.start_run.return_value = _run_out()

        resp = await client.post("/api/cycles/cyc-1/start")

    assert resp.status_code == 200
    assert resp.json()["id"] == "run-1"
    svc.start_run.assert_called_once_with("cyc-1", 1)


async def test_start_cycle_run_not_found(client):
    with patch("app.api.routers.cycle_runs.CycleRunService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.start_run.side_effect = HTTPException(status_code=404)

        resp = await client.post("/api/cycles/missing/start")

    assert resp.status_code == 404


async def test_start_cycle_run_private_forbidden(client):
    with patch("app.api.routers.cycle_runs.CycleRunService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.start_run.side_effect = HTTPException(status_code=403)

        resp = await client.post("/api/cycles/private/start")

    assert resp.status_code == 403


async def test_start_cycle_workout(client):
    result = {"run_id": "run-1", "log_id": "log-1", "workout_id": "w-1"}

    with patch("app.api.routers.cycle_runs.CycleRunService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.start_workout.return_value = result

        resp = await client.post(
            "/api/cycle-runs/run-1/workouts/cw-1/start",
            json={"notes": "Feeling good"},
        )

    assert resp.status_code == 200
    assert resp.json()["workout_id"] == "w-1"
    svc.start_workout.assert_called_once_with("run-1", "cw-1", "Feeling good", 1)


async def test_start_cycle_workout_run_not_found(client):
    with patch("app.api.routers.cycle_runs.CycleRunService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.start_workout.side_effect = HTTPException(status_code=404)

        resp = await client.post(
            "/api/cycle-runs/missing/workouts/cw-1/start", json={}
        )

    assert resp.status_code == 404


async def test_complete_cycle_workout(client):
    updated_run = _run_out()

    with patch("app.api.routers.cycle_runs.CycleRunService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.complete_workout.return_value = updated_run

        resp = await client.post(
            "/api/cycle-runs/run-1/workouts/cw-1/complete",
            json={"workout_id": "w-1"},
        )

    assert resp.status_code == 200
    svc.complete_workout.assert_called_once_with("run-1", "cw-1", "w-1", 1)


async def test_complete_cycle_workout_without_body(client):
    updated_run = _run_out()

    with patch("app.api.routers.cycle_runs.CycleRunService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.complete_workout.return_value = updated_run

        resp = await client.post("/api/cycle-runs/run-1/workouts/cw-1/complete")

    assert resp.status_code == 200
    # workout_id should be None when no body
    svc.complete_workout.assert_called_once_with("run-1", "cw-1", None, 1)


async def test_finish_cycle_run(client):
    finished = _run_out(completed_at=datetime(2026, 3, 1))

    with patch("app.api.routers.cycle_runs.CycleRunService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.finish_run.return_value = finished

        resp = await client.post("/api/cycle-runs/run-1/finish")

    assert resp.status_code == 200
    assert resp.json()["completed_at"] is not None
    svc.finish_run.assert_called_once_with("run-1", 1)


async def test_finish_cycle_run_not_found(client):
    with patch("app.api.routers.cycle_runs.CycleRunService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.finish_run.side_effect = HTTPException(status_code=404)

        resp = await client.post("/api/cycle-runs/missing/finish")

    assert resp.status_code == 404


@pytest.mark.parametrize("cycle_id", ["cyc-1", "cyc-abc", "some-uuid-here"])
async def test_get_active_run_various_cycle_ids(client, cycle_id):
    with patch("app.api.routers.cycle_runs.CycleRunService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_active_run.return_value = None

        resp = await client.get(f"/api/cycles/{cycle_id}/run")

    assert resp.status_code == 200
    svc.get_active_run.assert_called_once_with(cycle_id, 1)

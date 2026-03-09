"""Tests for /api/user router."""
from datetime import date, datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.api.schemas import UserOut, WeightEntryOut, GoalOut, UserMaxOut


def _user_out():
    return UserOut(name="Test User", age=25, avatarUrl=None, weightLog=[], goals=[], maxes=[])


def _weight_out():
    return WeightEntryOut(date=date(2026, 1, 1), kg=80.0)


def _goal_out():
    return GoalOut(id="g-1", text="Run 5k", targetDate=None, done=False)


def _max_out():
    return UserMaxOut(exercise_name="Bench Press", weight_kg=100.0, recorded_at=date(2026, 1, 1))


async def test_get_user(client):
    with patch("app.api.routers.users.UserService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_user.return_value = _user_out()

        resp = await client.get("/api/user")

    assert resp.status_code == 200
    assert resp.json()["name"] == "Test User"
    svc.get_user.assert_called_once_with(1)


async def test_update_profile(client):
    updated = UserOut(name="New Name", age=30, avatarUrl=None, weightLog=[], goals=[], maxes=[])

    with patch("app.api.routers.users.UserService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.update_profile.return_value = updated

        resp = await client.patch("/api/user/profile", json={"name": "New Name", "age": 30})

    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


async def test_log_weight(client):
    with patch("app.api.routers.users.UserService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.log_weight.return_value = _weight_out()

        resp = await client.post("/api/user/weight", json={"date": "2026-01-01", "kg": 80.0})

    assert resp.status_code == 200
    assert resp.json()["kg"] == 80.0


async def test_delete_weight(client):
    with patch("app.api.routers.users.UserService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc

        resp = await client.delete("/api/user/weight/2026-01-01")

    assert resp.status_code == 204
    svc.delete_weight.assert_called_once_with(1, "2026-01-01")


async def test_delete_weight_invalid_date_returns_422(client):
    with patch("app.api.routers.users.UserService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.delete_weight.side_effect = HTTPException(status_code=422, detail="Invalid date format")

        resp = await client.delete("/api/user/weight/not-a-date")

    assert resp.status_code == 422


async def test_create_goal(client):
    with patch("app.api.routers.users.UserService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.create_goal.return_value = _goal_out()

        resp = await client.post("/api/user/goals", json={"text": "Run 5k"})

    assert resp.status_code == 201
    assert resp.json()["text"] == "Run 5k"


async def test_toggle_goal(client):
    toggled = GoalOut(id="g-1", text="Run 5k", targetDate=None, done=True)

    with patch("app.api.routers.users.UserService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.toggle_goal.return_value = toggled

        resp = await client.patch("/api/user/goals/g-1/toggle")

    assert resp.status_code == 200
    assert resp.json()["done"] is True


async def test_toggle_goal_not_found_returns_404(client):
    with patch("app.api.routers.users.UserService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.toggle_goal.side_effect = HTTPException(status_code=404)

        resp = await client.patch("/api/user/goals/missing/toggle")

    assert resp.status_code == 404


async def test_delete_goal(client):
    with patch("app.api.routers.users.UserService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc

        resp = await client.delete("/api/user/goals/g-1")

    assert resp.status_code == 204


async def test_upsert_max(client):
    with patch("app.api.routers.users.UserService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.upsert_max.return_value = _max_out()

        resp = await client.post("/api/user/maxes", json={
            "exercise_name": "Bench Press", "weight_kg": 100.0
        })

    assert resp.status_code == 200
    assert resp.json()["weight_kg"] == 100.0


async def test_delete_max(client):
    with patch("app.api.routers.users.UserService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc

        resp = await client.delete("/api/user/maxes/Bench%20Press")

    assert resp.status_code == 204
    svc.delete_max.assert_called_once_with(1, "Bench Press")

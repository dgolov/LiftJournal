from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from app.api.schemas import AchievementOut


def _ach(id="first_workout", unlocked=True):
    return AchievementOut(
        id=id, title="Первый шаг", description="desc",
        icon="🎯", category="count", unlocked=unlocked,
        unlockedAt=datetime(2026, 1, 1) if unlocked else None,
    )


async def test_list_achievements(client):
    achievements = [_ach("first_workout"), _ach("workouts_10", unlocked=False)]

    with patch("app.api.routers.achievements.AchievementService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_all.return_value = achievements

        resp = await client.get("/api/achievements")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["id"] == "first_workout"
    assert data[0]["unlocked"] is True
    assert data[1]["unlocked"] is False
    svc.get_all.assert_called_once_with(1)


async def test_list_achievements_empty(client):
    with patch("app.api.routers.achievements.AchievementService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_all.return_value = []

        resp = await client.get("/api/achievements")

    assert resp.status_code == 200
    assert resp.json() == []


async def test_evaluate_achievements(client):
    newly = [_ach("first_workout")]

    with patch("app.api.routers.achievements.AchievementService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.evaluate.return_value = newly

        resp = await client.post("/api/achievements/evaluate")

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == "first_workout"
    svc.evaluate.assert_called_once_with(1)


async def test_evaluate_achievements_none_new(client):
    with patch("app.api.routers.achievements.AchievementService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.evaluate.return_value = []

        resp = await client.post("/api/achievements/evaluate")

    assert resp.status_code == 200
    assert resp.json() == []

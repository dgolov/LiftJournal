from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from app.api.schemas import NotificationOut, NotificationsPageOut, UnreadCountOut


def _notif(id="n-1", is_read=False):
    return NotificationOut(
        id=id, type="like", actorId=2, actorName="Alice",
        workoutId="w-1", workoutTitle="Bench day",
        commentText=None, isRead=is_read,
        createdAt=datetime(2026, 1, 1, 12, 0),
    )


async def test_get_unread_count(client):
    with patch("app.api.routers.notifications.NotificationService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_unread_count.return_value = UnreadCountOut(count=3)

        resp = await client.get("/api/notifications/unread-count")

    assert resp.status_code == 200
    assert resp.json()["count"] == 3
    svc.get_unread_count.assert_called_once_with(1)


async def test_get_unread_count_zero(client):
    with patch("app.api.routers.notifications.NotificationService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_unread_count.return_value = UnreadCountOut(count=0)

        resp = await client.get("/api/notifications/unread-count")

    assert resp.status_code == 200
    assert resp.json()["count"] == 0


async def test_get_notifications_default_params(client):
    page_out = NotificationsPageOut(items=[_notif()], hasMore=False, total=1)

    with patch("app.api.routers.notifications.NotificationService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_notifications.return_value = page_out

        resp = await client.get("/api/notifications")

    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["hasMore"] is False
    assert len(data["items"]) == 1
    svc.get_notifications.assert_called_once_with(1, False, 1, 20)


async def test_get_notifications_unread_only(client):
    page_out = NotificationsPageOut(items=[], hasMore=False, total=0)

    with patch("app.api.routers.notifications.NotificationService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_notifications.return_value = page_out

        resp = await client.get("/api/notifications?unread_only=true&page=2&per_page=10")

    assert resp.status_code == 200
    svc.get_notifications.assert_called_once_with(1, True, 2, 10)


async def test_mark_all_read(client):
    with patch("app.api.routers.notifications.NotificationService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.mark_all_read.return_value = None

        resp = await client.post("/api/notifications/read-all")

    assert resp.status_code == 204
    svc.mark_all_read.assert_called_once_with(1)


async def test_mark_one_read(client):
    with patch("app.api.routers.notifications.NotificationService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.mark_read.return_value = None

        resp = await client.patch("/api/notifications/n-42/read")

    assert resp.status_code == 204
    svc.mark_read.assert_called_once_with("n-42", 1)

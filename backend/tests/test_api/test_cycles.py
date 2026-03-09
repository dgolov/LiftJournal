"""Tests for /api/cycles router."""
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.api.schemas import CycleListOut, CycleDetailOut


def _cycle_list_out(id="cyc-1", title="5/3/1"):
    return CycleListOut(
        id=id, title=title, description="", author_name="",
        created_by=1, is_public=True,
        created_at=datetime(2026, 1, 1), workout_count=3,
    )


def _cycle_detail_out(id="cyc-1", title="5/3/1"):
    return CycleDetailOut(
        id=id, title=title, description="", author_name="",
        created_by=1, is_public=True,
        created_at=datetime(2026, 1, 1), workouts=[],
    )


async def test_list_cycles(client):
    cycles = [_cycle_list_out("cyc-1"), _cycle_list_out("cyc-2")]

    with patch("app.api.routers.cycles.CycleService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.list_cycles.return_value = cycles

        resp = await client.get("/api/cycles")

    assert resp.status_code == 200
    assert len(resp.json()) == 2
    svc.list_cycles.assert_called_once_with(1)


async def test_list_cycles_empty(client):
    with patch("app.api.routers.cycles.CycleService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.list_cycles.return_value = []

        resp = await client.get("/api/cycles")

    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_cycle(client):
    with patch("app.api.routers.cycles.CycleService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.create_cycle.return_value = _cycle_detail_out()

        resp = await client.post("/api/cycles", json={"title": "5/3/1", "is_public": True})

    assert resp.status_code == 201
    assert resp.json()["id"] == "cyc-1"
    svc.create_cycle.assert_called_once()


async def test_create_cycle_missing_title_returns_422(client):
    resp = await client.post("/api/cycles", json={"is_public": True})
    assert resp.status_code == 422


async def test_get_cycle(client):
    with patch("app.api.routers.cycles.CycleService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_cycle.return_value = _cycle_detail_out()

        resp = await client.get("/api/cycles/cyc-1")

    assert resp.status_code == 200
    svc.get_cycle.assert_called_once_with("cyc-1", 1)


async def test_get_cycle_not_found(client):
    with patch("app.api.routers.cycles.CycleService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_cycle.side_effect = HTTPException(status_code=404)

        resp = await client.get("/api/cycles/missing")

    assert resp.status_code == 404


async def test_get_cycle_private_forbidden(client):
    with patch("app.api.routers.cycles.CycleService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_cycle.side_effect = HTTPException(status_code=403)

        resp = await client.get("/api/cycles/private-cyc")

    assert resp.status_code == 403


async def test_update_cycle(client):
    updated = _cycle_detail_out(title="Updated")

    with patch("app.api.routers.cycles.CycleService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.update_cycle.return_value = updated

        resp = await client.patch("/api/cycles/cyc-1", json={"title": "Updated"})

    assert resp.status_code == 200
    svc.update_cycle.assert_called_once()


async def test_update_cycle_not_owner_returns_403(client):
    with patch("app.api.routers.cycles.CycleService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.update_cycle.side_effect = HTTPException(status_code=403)

        resp = await client.patch("/api/cycles/cyc-other", json={"title": "Hack"})

    assert resp.status_code == 403


async def test_delete_cycle(client):
    with patch("app.api.routers.cycles.CycleService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc

        resp = await client.delete("/api/cycles/cyc-1")

    assert resp.status_code == 204
    svc.delete_cycle.assert_called_once_with("cyc-1", 1)


async def test_delete_cycle_not_found(client):
    with patch("app.api.routers.cycles.CycleService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.delete_cycle.side_effect = HTTPException(status_code=404)

        resp = await client.delete("/api/cycles/missing")

    assert resp.status_code == 404


@pytest.mark.parametrize("is_public", [True, False])
async def test_create_cycle_public_flag(client, is_public):
    detail = _cycle_detail_out()
    detail.is_public = is_public

    with patch("app.api.routers.cycles.CycleService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.create_cycle.return_value = detail

        resp = await client.post("/api/cycles", json={"title": "Prog", "is_public": is_public})

    assert resp.status_code == 201

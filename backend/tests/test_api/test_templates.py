from datetime import datetime
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from app.api.schemas import WorkoutTemplateOut


def _template(id="tpl-1", title="Push day"):
    return WorkoutTemplateOut(
        id=id, title=title, type="Силовая",
        createdAt=datetime(2026, 1, 1), exercises=[],
    )


async def test_list_templates(client):
    templates = [_template("tpl-1"), _template("tpl-2")]

    with patch("app.api.routers.templates.TemplateService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_all.return_value = templates

        resp = await client.get("/api/templates")

    assert resp.status_code == 200
    assert len(resp.json()) == 2
    svc.get_all.assert_called_once_with(1)


async def test_list_templates_empty(client):
    with patch("app.api.routers.templates.TemplateService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_all.return_value = []

        resp = await client.get("/api/templates")

    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_template(client):
    with patch("app.api.routers.templates.TemplateService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.create.return_value = _template()

        resp = await client.post("/api/templates", json={
            "title": "Push day",
            "type": "Силовая",
            "exercises": [
                {"exerciseId": "ex-1", "exerciseName": "Bench Press", "targetSets": 4}
            ],
        })

    assert resp.status_code == 201
    assert resp.json()["id"] == "tpl-1"
    svc.create.assert_called_once()


async def test_create_template_missing_required_returns_422(client):
    resp = await client.post("/api/templates", json={"exercises": []})
    assert resp.status_code == 422


async def test_update_template(client):
    with patch("app.api.routers.templates.TemplateService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.update.return_value = _template(title="Pull day")

        resp = await client.patch("/api/templates/tpl-1", json={"title": "Pull day"})

    assert resp.status_code == 200
    assert resp.json()["title"] == "Pull day"
    svc.update.assert_called_once()


async def test_update_template_not_found(client):
    with patch("app.api.routers.templates.TemplateService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.update.side_effect = HTTPException(status_code=404, detail="Template not found")

        resp = await client.patch("/api/templates/missing", json={"title": "x"})

    assert resp.status_code == 404


async def test_delete_template(client):
    with patch("app.api.routers.templates.TemplateService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.delete.return_value = None

        resp = await client.delete("/api/templates/tpl-1")

    assert resp.status_code == 204
    svc.delete.assert_called_once_with("tpl-1", 1)


async def test_delete_template_not_found(client):
    with patch("app.api.routers.templates.TemplateService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.delete.side_effect = HTTPException(status_code=404, detail="Template not found")

        resp = await client.delete("/api/templates/missing")

    assert resp.status_code == 404

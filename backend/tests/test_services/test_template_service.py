from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.schemas import WorkoutTemplateCreate, WorkoutTemplateUpdate
from app.services.template import TemplateService


@pytest.fixture
def mock_db():
    return AsyncMock()


def _make_template(id="tpl-1", user_id=1):
    t = MagicMock()
    t.id = id
    t.user_id = user_id
    t.title = "Push day"
    t.type = "Силовая"
    t.created_at = datetime(2026, 1, 1)
    t.exercises = []
    return t


# ---------------------------------------------------------------------------
# get_all — must only ever query by the requesting user's id
# ---------------------------------------------------------------------------

async def test_get_all_scoped_to_requesting_user(mock_db):
    with patch("app.services.template.TemplateRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_all_by_user.return_value = [_make_template(user_id=42)]

        await TemplateService(mock_db).get_all(42)

    repo.get_all_by_user.assert_called_once_with(42)


# ---------------------------------------------------------------------------
# update / delete — another user's template must be rejected, not just hidden
# ---------------------------------------------------------------------------

async def test_update_other_users_template_forbidden(mock_db):
    other_users_template = _make_template(user_id=1)

    with patch("app.services.template.TemplateRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = other_users_template

        with pytest.raises(HTTPException) as exc_info:
            await TemplateService(mock_db).update(
                "tpl-1", WorkoutTemplateUpdate(title="Hijacked"), user_id=999
            )

    assert exc_info.value.status_code == 403
    repo.update.assert_not_called()


async def test_delete_other_users_template_forbidden(mock_db):
    other_users_template = _make_template(user_id=1)

    with patch("app.services.template.TemplateRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = other_users_template

        with pytest.raises(HTTPException) as exc_info:
            await TemplateService(mock_db).delete("tpl-1", user_id=999)

    assert exc_info.value.status_code == 403
    repo.delete.assert_not_called()


async def test_update_own_template_succeeds(mock_db):
    own_template = _make_template(user_id=1)

    with patch("app.services.template.TemplateRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = own_template
        repo.update.return_value = own_template

        result = await TemplateService(mock_db).update(
            "tpl-1", WorkoutTemplateUpdate(title="Renamed"), user_id=1
        )

    assert result.id == "tpl-1"
    repo.update.assert_called_once()


async def test_create_assigns_requesting_user(mock_db):
    with patch("app.services.template.TemplateRepository") as MockRepo:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.create.return_value = _make_template(user_id=7)

        await TemplateService(mock_db).create(
            WorkoutTemplateCreate(title="Push day", exercises=[]), user_id=7
        )

    _, kwargs = repo.create.call_args
    assert kwargs["user_id"] == 7

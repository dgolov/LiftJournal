from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.api.schemas import AdminUserOut, AdminExerciseOut
from tests.conftest import make_user


@pytest.fixture
def current_user():
    return make_user(id=1, name="Admin", email="admin@test.com", is_admin=True)


def _user_out(id=1, email="a@test.com", name="A", is_admin=False):
    return AdminUserOut(id=id, email=email, name=name, isAdmin=is_admin)


def _exercise_out(id="ex-1", name="Bench Press", is_approved=False):
    return AdminExerciseOut(
        id=id, name=name, muscleGroup="Грудь", secondaryMuscles=[],
        equipment="Штанга", description="", isApproved=is_approved,
        submittedByName="User", submittedByEmail="user@test.com",
    )


async def test_list_users(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.list_users.return_value = [_user_out(1), _user_out(2)]

        resp = await client.get("/api/admin/users")

    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_list_pending_exercises(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.list_pending_exercises.return_value = [_exercise_out()]

        resp = await client.get("/api/admin/exercises/pending")

    assert resp.status_code == 200
    assert resp.json()[0]["id"] == "ex-1"


async def test_approve_exercise(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.approve_exercise.return_value = _exercise_out(is_approved=True)

        resp = await client.post("/api/admin/exercises/ex-1/approve")

    assert resp.status_code == 200
    assert resp.json()["isApproved"] is True


async def test_approve_exercise_not_found(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.approve_exercise.side_effect = HTTPException(status_code=404, detail="Exercise not found")

        resp = await client.post("/api/admin/exercises/missing/approve")

    assert resp.status_code == 404


async def test_reject_exercise(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.reject_exercise.return_value = None

        resp = await client.delete("/api/admin/exercises/ex-1")

    assert resp.status_code == 204


class TestNonAdminAccess:
    """Non-admin routes must 404, not 401/403 — the admin API should look
    like it doesn't exist at all to a regular authenticated user."""

    @pytest.fixture
    def current_user(self):
        return make_user(id=2, name="Regular", email="user@test.com", is_admin=False)

    async def test_users_hidden_from_non_admin(self, client):
        resp = await client.get("/api/admin/users")
        assert resp.status_code == 404

    async def test_pending_exercises_hidden_from_non_admin(self, client):
        resp = await client.get("/api/admin/exercises/pending")
        assert resp.status_code == 404

    async def test_approve_hidden_from_non_admin(self, client):
        resp = await client.post("/api/admin/exercises/ex-1/approve")
        assert resp.status_code == 404

    async def test_reject_hidden_from_non_admin(self, client):
        resp = await client.delete("/api/admin/exercises/ex-1")
        assert resp.status_code == 404

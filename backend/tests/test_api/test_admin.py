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


def _exercise_out(id="ex-1", name="Bench Press", is_approved=False, is_private=False):
    return AdminExerciseOut(
        id=id, name=name, muscleGroup="Грудь", secondaryMuscles=[],
        equipment="Штанга", description="", isApproved=is_approved, isPrivate=is_private,
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


async def test_list_exercises_pending(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.list_exercises.return_value = [_exercise_out()]

        resp = await client.get("/api/admin/exercises")

    assert resp.status_code == 200
    assert resp.json()[0]["id"] == "ex-1"
    svc.list_exercises.assert_called_once_with("pending")


async def test_list_exercises_all(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.list_exercises.return_value = [_exercise_out(is_approved=True)]

        resp = await client.get("/api/admin/exercises?status=all")

    assert resp.status_code == 200
    svc.list_exercises.assert_called_once_with("all")


async def test_list_exercises_invalid_status_returns_422(client):
    resp = await client.get("/api/admin/exercises?status=bogus")
    assert resp.status_code == 422


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


async def test_revoke_exercise(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.revoke_exercise.return_value = _exercise_out(is_private=True)

        resp = await client.post("/api/admin/exercises/ex-1/revoke")

    assert resp.status_code == 200
    assert resp.json()["isPrivate"] is True


async def test_rename_exercise(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.rename_exercise.return_value = _exercise_out(name="New Name")

        resp = await client.patch("/api/admin/exercises/ex-1", json={"name": "New Name"})

    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"
    svc.rename_exercise.assert_called_once_with("ex-1", "New Name")


async def test_rename_exercise_missing_name_returns_422(client):
    resp = await client.patch("/api/admin/exercises/ex-1", json={})
    assert resp.status_code == 422


async def test_reject_exercise(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.reject_exercise.return_value = None

        resp = await client.delete("/api/admin/exercises/ex-1")

    assert resp.status_code == 204


async def test_reject_public_exercise_returns_400(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.reject_exercise.side_effect = HTTPException(
            status_code=400, detail="Нельзя удалить опубликованное упражнение"
        )

        resp = await client.delete("/api/admin/exercises/ex-1")

    assert resp.status_code == 400


class TestNonAdminAccess:
    """Non-admin routes must 404, not 401/403 — the admin API should look
    like it doesn't exist at all to a regular authenticated user."""

    @pytest.fixture
    def current_user(self):
        return make_user(id=2, name="Regular", email="user@test.com", is_admin=False)

    async def test_users_hidden_from_non_admin(self, client):
        resp = await client.get("/api/admin/users")
        assert resp.status_code == 404

    async def test_exercises_hidden_from_non_admin(self, client):
        resp = await client.get("/api/admin/exercises")
        assert resp.status_code == 404

    async def test_approve_hidden_from_non_admin(self, client):
        resp = await client.post("/api/admin/exercises/ex-1/approve")
        assert resp.status_code == 404

    async def test_revoke_hidden_from_non_admin(self, client):
        resp = await client.post("/api/admin/exercises/ex-1/revoke")
        assert resp.status_code == 404

    async def test_rename_hidden_from_non_admin(self, client):
        resp = await client.patch("/api/admin/exercises/ex-1", json={"name": "X"})
        assert resp.status_code == 404

    async def test_reject_hidden_from_non_admin(self, client):
        resp = await client.delete("/api/admin/exercises/ex-1")
        assert resp.status_code == 404

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.api.schemas import (
    AdminUserOut, AdminExerciseOut, AdminCycleOut, AdminStatsOut, DailyCountOut, TopUserOut,
)
from tests.conftest import make_user


@pytest.fixture
def current_user():
    return make_user(id=1, name="Admin", email="admin@test.com", is_admin=True)


def _user_out(id=1, email="a@test.com", name="A", is_admin=False):
    return AdminUserOut(id=id, email=email, name=name, isAdmin=is_admin)


def _exercise_out(id="ex-1", name="Bench Press", status="pending"):
    return AdminExerciseOut(
        id=id, name=name, muscleGroup="Грудь", secondaryMuscles=[],
        equipment="Штанга", description="", status=status,
        submittedByName="User", submittedByEmail="user@test.com",
    )


def _cycle_out(id="cyc-1", title="5/3/1", is_public=True, is_approved=False):
    return AdminCycleOut(
        id=id, title=title, description="", authorName="Jim Wendler",
        isPublic=is_public, isApproved=is_approved, workoutCount=3,
        createdAt=datetime(2026, 1, 1),
        submittedByName="User", submittedByEmail="user@test.com",
    )


def _stats_out():
    return AdminStatsOut(
        totalUsers=5, newUsersLast7Days=2, totalWorkouts=50, workoutsLast7Days=3,
        totalExercises=39, customExercises=1, pendingExercises=0,
        totalCycles=2, publicCycles=2, pendingCycles=0,
        dailyWorkouts=[DailyCountOut(date="2026-08-23", count=1)],
        topUsers=[TopUserOut(id=2, name="Дмитрий", workoutCount=31)],
    )


async def test_list_users(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.list_users.return_value = [_user_out(1), _user_out(2)]

        resp = await client.get("/api/admin/users")

    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_get_stats(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_stats.return_value = _stats_out()

        resp = await client.get("/api/admin/stats")

    assert resp.status_code == 200
    body = resp.json()
    assert body["totalUsers"] == 5
    assert body["topUsers"][0]["name"] == "Дмитрий"
    assert body["dailyWorkouts"][0]["date"] == "2026-08-23"


async def test_set_user_admin_grants(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.set_user_admin.return_value = _user_out(2, is_admin=True)

        resp = await client.patch("/api/admin/users/2", json={"isAdmin": True})

    assert resp.status_code == 200
    assert resp.json()["isAdmin"] is True
    svc.set_user_admin.assert_called_once_with(2, True, 1)


async def test_set_user_admin_self_demotion_returns_400(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.set_user_admin.side_effect = HTTPException(
            status_code=400, detail="Нельзя снять права администратора с самого себя"
        )

        resp = await client.patch("/api/admin/users/1", json={"isAdmin": False})

    assert resp.status_code == 400


async def test_set_user_admin_not_found(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.set_user_admin.side_effect = HTTPException(status_code=404, detail="User not found")

        resp = await client.patch("/api/admin/users/999", json={"isAdmin": True})

    assert resp.status_code == 404


async def test_list_exercises_pending(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.list_exercises.return_value = [_exercise_out()]

        resp = await client.get("/api/admin/exercises")

    assert resp.status_code == 200
    assert resp.json()[0]["id"] == "ex-1"
    svc.list_exercises.assert_called_once_with("pending", None, None)


async def test_list_exercises_with_search_and_muscle_group(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.list_exercises.return_value = [_exercise_out(status="approved")]

        resp = await client.get("/api/admin/exercises?status=all&search=Bench&muscleGroup=%D0%93%D1%80%D1%83%D0%B4%D1%8C")

    assert resp.status_code == 200
    svc.list_exercises.assert_called_once_with("all", "Bench", "Грудь")


async def test_list_exercises_rejected_status(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.list_exercises.return_value = [_exercise_out(status="rejected")]

        resp = await client.get("/api/admin/exercises?status=rejected")

    assert resp.status_code == 200
    assert resp.json()[0]["status"] == "rejected"
    svc.list_exercises.assert_called_once_with("rejected", None, None)


async def test_list_exercises_all(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.list_exercises.return_value = [_exercise_out(status="approved")]

        resp = await client.get("/api/admin/exercises?status=all")

    assert resp.status_code == 200
    svc.list_exercises.assert_called_once_with("all", None, None)


async def test_list_exercises_invalid_status_returns_422(client):
    resp = await client.get("/api/admin/exercises?status=bogus")
    assert resp.status_code == 422


async def test_approve_exercise(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.approve_exercise.return_value = _exercise_out(status="approved")

        resp = await client.post("/api/admin/exercises/ex-1/approve")

    assert resp.status_code == 200
    assert resp.json()["status"] == "approved"


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
        svc.revoke_exercise.return_value = _exercise_out(status="private")

        resp = await client.post("/api/admin/exercises/ex-1/revoke")

    assert resp.status_code == 200
    assert resp.json()["status"] == "private"


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


async def test_list_cycles_pending(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.list_cycles.return_value = [_cycle_out()]

        resp = await client.get("/api/admin/cycles")

    assert resp.status_code == 200
    assert resp.json()[0]["id"] == "cyc-1"
    svc.list_cycles.assert_called_once_with("pending")


async def test_list_cycles_all(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.list_cycles.return_value = [_cycle_out(is_approved=True)]

        resp = await client.get("/api/admin/cycles?status=all")

    assert resp.status_code == 200
    svc.list_cycles.assert_called_once_with("all")


async def test_approve_cycle(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.approve_cycle.return_value = _cycle_out(is_approved=True)

        resp = await client.post("/api/admin/cycles/cyc-1/approve")

    assert resp.status_code == 200
    assert resp.json()["isApproved"] is True


async def test_approve_cycle_not_found(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.approve_cycle.side_effect = HTTPException(status_code=404, detail="Cycle not found")

        resp = await client.post("/api/admin/cycles/missing/approve")

    assert resp.status_code == 404


async def test_revoke_cycle(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.revoke_cycle.return_value = _cycle_out(is_public=False, is_approved=False)

        resp = await client.post("/api/admin/cycles/cyc-1/revoke")

    assert resp.status_code == 200
    assert resp.json()["isPublic"] is False


async def test_reject_cycle(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.reject_cycle.return_value = None

        resp = await client.delete("/api/admin/cycles/cyc-1")

    assert resp.status_code == 204


async def test_reject_public_cycle_returns_400(client):
    with patch("app.api.routers.admin.AdminService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.reject_cycle.side_effect = HTTPException(
            status_code=400, detail="Нельзя удалить опубликованный цикл"
        )

        resp = await client.delete("/api/admin/cycles/cyc-1")

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

    async def test_set_user_admin_hidden_from_non_admin(self, client):
        resp = await client.patch("/api/admin/users/1", json={"isAdmin": True})
        assert resp.status_code == 404

    async def test_stats_hidden_from_non_admin(self, client):
        resp = await client.get("/api/admin/stats")
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

    async def test_cycles_hidden_from_non_admin(self, client):
        resp = await client.get("/api/admin/cycles")
        assert resp.status_code == 404

    async def test_approve_cycle_hidden_from_non_admin(self, client):
        resp = await client.post("/api/admin/cycles/cyc-1/approve")
        assert resp.status_code == 404

    async def test_revoke_cycle_hidden_from_non_admin(self, client):
        resp = await client.post("/api/admin/cycles/cyc-1/revoke")
        assert resp.status_code == 404

    async def test_reject_cycle_hidden_from_non_admin(self, client):
        resp = await client.delete("/api/admin/cycles/cyc-1")
        assert resp.status_code == 404

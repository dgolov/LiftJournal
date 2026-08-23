from datetime import date, datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.services.admin import AdminService
from tests.conftest import make_user, make_exercise, make_cycle


@pytest.fixture
def mock_db():
    return AsyncMock()


class TestListUsers:
    async def test_maps_users_to_dto(self, mock_db):
        users = [
            make_user(id=1, email="a@test.com", name="A", is_admin=True),
            make_user(id=2, email="b@test.com", name="B", is_admin=False),
        ]
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_all_users.return_value = users

            result = await AdminService(mock_db).list_users()

        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].isAdmin is True
        assert result[1].isAdmin is False


class TestSetUserAdmin:
    async def test_grants_admin(self, mock_db):
        user = make_user(id=2, name="B", email="b@test.com", is_admin=False)
        updated = make_user(id=2, name="B", email="b@test.com", is_admin=True)
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_user_by_id.return_value = user
            repo.set_user_admin.return_value = updated

            result = await AdminService(mock_db).set_user_admin(2, True, current_admin_id=1)

        assert result.isAdmin is True
        repo.set_user_admin.assert_called_once_with(user, True)

    async def test_revokes_admin_from_another_user(self, mock_db):
        user = make_user(id=2, is_admin=True)
        updated = make_user(id=2, is_admin=False)
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_user_by_id.return_value = user
            repo.set_user_admin.return_value = updated

            result = await AdminService(mock_db).set_user_admin(2, False, current_admin_id=1)

        assert result.isAdmin is False

    async def test_refuses_self_demotion(self, mock_db):
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo

            with pytest.raises(HTTPException) as exc_info:
                await AdminService(mock_db).set_user_admin(1, False, current_admin_id=1)

        assert exc_info.value.status_code == 400
        repo.get_user_by_id.assert_not_called()

    async def test_allows_self_grant(self, mock_db):
        """Granting yourself admin (already true, no-op in practice) isn't blocked
        by the self-demotion guard — only removing your own admin status is."""
        user = make_user(id=1, is_admin=True)
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_user_by_id.return_value = user
            repo.set_user_admin.return_value = user

            result = await AdminService(mock_db).set_user_admin(1, True, current_admin_id=1)

        assert result.isAdmin is True

    async def test_not_found(self, mock_db):
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_user_by_id.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await AdminService(mock_db).set_user_admin(999, True, current_admin_id=1)

        assert exc_info.value.status_code == 404


class TestResetPassword:
    async def test_success(self, mock_db):
        user = make_user(id=2)
        with patch("app.services.admin.AdminRepository") as MockRepo, \
             patch("app.services.admin.hash_password") as mock_hash:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_user_by_id.return_value = user
            mock_hash.return_value = "$2b$12$newhash"

            await AdminService(mock_db).reset_password(2, "newpass123")

        mock_hash.assert_called_once_with("newpass123")
        repo.set_password.assert_called_once_with(user, "$2b$12$newhash")

    async def test_too_short_returns_422(self, mock_db):
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo

            with pytest.raises(HTTPException) as exc_info:
                await AdminService(mock_db).reset_password(2, "abc")

        assert exc_info.value.status_code == 422
        repo.get_user_by_id.assert_not_called()

    async def test_not_found(self, mock_db):
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_user_by_id.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await AdminService(mock_db).reset_password(999, "newpass123")

        assert exc_info.value.status_code == 404


class TestListExercises:
    async def test_includes_submitter_info(self, mock_db):
        ex = make_exercise(id="ex-1", name="Cable Fly", status="pending", created_by=5)
        submitter = make_user(id=5, name="Alex", email="alex@test.com")
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_exercises.return_value = [(ex, submitter)]

            result = await AdminService(mock_db).list_exercises()

        assert len(result) == 1
        assert result[0].id == "ex-1"
        assert result[0].status == "pending"
        assert result[0].submittedByName == "Alex"
        assert result[0].submittedByEmail == "alex@test.com"
        repo.get_exercises.assert_called_once_with(status="pending", search=None, muscle_group=None)

    async def test_handles_missing_submitter(self, mock_db):
        ex = make_exercise(id="ex-1", status="pending", created_by=None)
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_exercises.return_value = [(ex, None)]

            result = await AdminService(mock_db).list_exercises()

        assert result[0].submittedByName is None
        assert result[0].submittedByEmail is None

    async def test_status_all_passes_through(self, mock_db):
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_exercises.return_value = []

            await AdminService(mock_db).list_exercises("all")

        repo.get_exercises.assert_called_once_with(status="all", search=None, muscle_group=None)

    async def test_search_and_muscle_group_pass_through(self, mock_db):
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_exercises.return_value = []

            await AdminService(mock_db).list_exercises("all", "Bench", "Грудь")

        repo.get_exercises.assert_called_once_with(status="all", search="Bench", muscle_group="Грудь")


class TestApproveExercise:
    async def test_success(self, mock_db):
        ex = make_exercise(id="ex-1", status="pending")
        approved = make_exercise(id="ex-1", status="approved")
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_exercise_by_id.return_value = ex
            repo.approve_exercise.return_value = approved

            result = await AdminService(mock_db).approve_exercise("ex-1")

        assert result.status == "approved"
        repo.approve_exercise.assert_called_once_with(ex)

    async def test_not_found(self, mock_db):
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_exercise_by_id.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await AdminService(mock_db).approve_exercise("missing")

        assert exc_info.value.status_code == 404


class TestRevokeExercise:
    async def test_success(self, mock_db):
        ex = make_exercise(id="ex-1", status="approved")
        revoked = make_exercise(id="ex-1", status="private")
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_exercise_by_id.return_value = ex
            repo.revoke_exercise.return_value = revoked

            result = await AdminService(mock_db).revoke_exercise("ex-1")

        assert result.status == "private"
        repo.revoke_exercise.assert_called_once_with(ex)

    async def test_not_found(self, mock_db):
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_exercise_by_id.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await AdminService(mock_db).revoke_exercise("missing")

        assert exc_info.value.status_code == 404


class TestRenameExercise:
    async def test_success(self, mock_db):
        ex = make_exercise(id="ex-1", name="Old")
        renamed = make_exercise(id="ex-1", name="New")
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_exercise_by_id.return_value = ex
            repo.rename_exercise.return_value = renamed

            result = await AdminService(mock_db).rename_exercise("ex-1", "New")

        assert result.name == "New"
        repo.rename_exercise.assert_called_once_with(ex, "New")

    async def test_not_found(self, mock_db):
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_exercise_by_id.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await AdminService(mock_db).rename_exercise("missing", "New")

        assert exc_info.value.status_code == 404


class TestRejectExercise:
    async def test_success_for_pending(self, mock_db):
        ex = make_exercise(id="ex-1", status="pending")
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_exercise_by_id.return_value = ex

            await AdminService(mock_db).reject_exercise("ex-1")

        repo.reject_exercise.assert_called_once_with(ex)

    async def test_refuses_to_reject_private_exercise(self, mock_db):
        """Private exercises were never submitted for review — nothing to reject."""
        ex = make_exercise(id="ex-1", status="private")
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_exercise_by_id.return_value = ex

            with pytest.raises(HTTPException) as exc_info:
                await AdminService(mock_db).reject_exercise("ex-1")

        assert exc_info.value.status_code == 400
        repo.reject_exercise.assert_not_called()

    async def test_refuses_to_reject_approved_exercise(self, mock_db):
        ex = make_exercise(id="ex-1", status="approved")
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_exercise_by_id.return_value = ex

            with pytest.raises(HTTPException) as exc_info:
                await AdminService(mock_db).reject_exercise("ex-1")

        assert exc_info.value.status_code == 400
        repo.reject_exercise.assert_not_called()

    async def test_refuses_to_reject_already_rejected_exercise(self, mock_db):
        ex = make_exercise(id="ex-1", status="rejected")
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_exercise_by_id.return_value = ex

            with pytest.raises(HTTPException) as exc_info:
                await AdminService(mock_db).reject_exercise("ex-1")

        assert exc_info.value.status_code == 400

    async def test_not_found(self, mock_db):
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_exercise_by_id.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await AdminService(mock_db).reject_exercise("missing")

        assert exc_info.value.status_code == 404


class TestListCycles:
    async def test_includes_submitter_and_workout_count(self, mock_db):
        c = make_cycle(id="cyc-1", is_public=True, is_approved=False, created_by=5)
        submitter = make_user(id=5, name="Alex", email="alex@test.com")
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_cycles.return_value = ([(c, submitter)], {"cyc-1": 4})

            result = await AdminService(mock_db).list_cycles()

        assert len(result) == 1
        assert result[0].id == "cyc-1"
        assert result[0].workoutCount == 4
        assert result[0].submittedByName == "Alex"
        repo.get_cycles.assert_called_once_with(pending_only=True)

    async def test_status_all_passes_through(self, mock_db):
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_cycles.return_value = ([], {})

            await AdminService(mock_db).list_cycles("all")

        repo.get_cycles.assert_called_once_with(pending_only=False)


class TestApproveCycle:
    async def test_success(self, mock_db):
        c = make_cycle(id="cyc-1", is_approved=False)
        approved = make_cycle(id="cyc-1", is_approved=True)
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_cycle_by_id.return_value = c
            repo.approve_cycle.return_value = approved

            result = await AdminService(mock_db).approve_cycle("cyc-1")

        assert result.isApproved is True
        repo.approve_cycle.assert_called_once_with(c)

    async def test_not_found(self, mock_db):
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_cycle_by_id.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await AdminService(mock_db).approve_cycle("missing")

        assert exc_info.value.status_code == 404


class TestRevokeCycle:
    async def test_success(self, mock_db):
        c = make_cycle(id="cyc-1", is_public=True, is_approved=True)
        revoked = make_cycle(id="cyc-1", is_public=False, is_approved=False)
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_cycle_by_id.return_value = c
            repo.revoke_cycle.return_value = revoked

            result = await AdminService(mock_db).revoke_cycle("cyc-1")

        assert result.isPublic is False
        repo.revoke_cycle.assert_called_once_with(c)

    async def test_not_found(self, mock_db):
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_cycle_by_id.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await AdminService(mock_db).revoke_cycle("missing")

        assert exc_info.value.status_code == 404


class TestRejectCycle:
    async def test_success_for_pending(self, mock_db):
        c = make_cycle(id="cyc-1", is_public=True, is_approved=False)
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_cycle_by_id.return_value = c

            await AdminService(mock_db).reject_cycle("cyc-1")

        repo.delete_cycle.assert_called_once_with(c)

    async def test_refuses_to_delete_public_approved_cycle(self, mock_db):
        c = make_cycle(id="cyc-1", is_public=True, is_approved=True)
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_cycle_by_id.return_value = c

            with pytest.raises(HTTPException) as exc_info:
                await AdminService(mock_db).reject_cycle("cyc-1")

        assert exc_info.value.status_code == 400
        repo.delete_cycle.assert_not_called()

    async def test_not_found(self, mock_db):
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_cycle_by_id.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await AdminService(mock_db).reject_cycle("missing")

        assert exc_info.value.status_code == 404


class TestGetStats:
    async def _run(self, mock_db, stats_data):
        with patch("app.services.admin.AdminRepository") as MockRepo, \
             patch("app.services.admin.datetime") as MockDatetime:
            MockDatetime.utcnow.return_value = datetime(2026, 8, 23)
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_stats_data.return_value = stats_data

            return await AdminService(mock_db).get_stats()

    async def test_maps_counts(self, mock_db):
        result = await self._run(mock_db, {
            "total_users": 5, "new_users_7d": 2, "total_workouts": 50, "workouts_7d": 3,
            "total_exercises": 39, "custom_exercises": 1, "pending_exercises": 0,
            "total_cycles": 2, "public_cycles": 2, "pending_cycles": 0,
            "daily_rows": [], "top_rows": [],
        })

        assert result.totalUsers == 5
        assert result.newUsersLast7Days == 2
        assert result.totalWorkouts == 50
        assert result.workoutsLast7Days == 3
        assert result.totalExercises == 39
        assert result.customExercises == 1
        assert result.pendingExercises == 0
        assert result.totalCycles == 2
        assert result.publicCycles == 2
        assert result.pendingCycles == 0

    async def test_daily_workouts_zero_fills_missing_days(self, mock_db):
        result = await self._run(mock_db, {
            "total_users": 0, "new_users_7d": 0, "total_workouts": 0, "workouts_7d": 0,
            "total_exercises": 0, "custom_exercises": 0, "pending_exercises": 0,
            "total_cycles": 0, "public_cycles": 0, "pending_cycles": 0,
            "daily_rows": [(date(2026, 8, 21), 4), (date(2026, 8, 23), 1)],
            "top_rows": [],
        })

        assert len(result.dailyWorkouts) == 14
        assert result.dailyWorkouts[0].date == "2026-08-10"
        assert result.dailyWorkouts[-1].date == "2026-08-23"
        by_date = {d.date: d.count for d in result.dailyWorkouts}
        assert by_date["2026-08-21"] == 4
        assert by_date["2026-08-23"] == 1
        assert by_date["2026-08-22"] == 0
        assert by_date["2026-08-10"] == 0

    async def test_top_users_mapped(self, mock_db):
        result = await self._run(mock_db, {
            "total_users": 0, "new_users_7d": 0, "total_workouts": 0, "workouts_7d": 0,
            "total_exercises": 0, "custom_exercises": 0, "pending_exercises": 0,
            "total_cycles": 0, "public_cycles": 0, "pending_cycles": 0,
            "daily_rows": [], "top_rows": [(2, 31, "Дмитрий"), (3, 2, "Test")],
        })

        assert len(result.topUsers) == 2
        assert result.topUsers[0].id == 2
        assert result.topUsers[0].name == "Дмитрий"
        assert result.topUsers[0].workoutCount == 31

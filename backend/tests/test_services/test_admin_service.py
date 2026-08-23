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

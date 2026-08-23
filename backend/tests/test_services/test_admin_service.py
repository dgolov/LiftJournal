from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.services.admin import AdminService
from tests.conftest import make_user, make_exercise


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


class TestListPendingExercises:
    async def test_includes_submitter_info(self, mock_db):
        ex = make_exercise(id="ex-1", name="Cable Fly", is_approved=False, created_by=5)
        submitter = make_user(id=5, name="Alex", email="alex@test.com")
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_pending_exercises.return_value = [(ex, submitter)]

            result = await AdminService(mock_db).list_pending_exercises()

        assert len(result) == 1
        assert result[0].id == "ex-1"
        assert result[0].isApproved is False
        assert result[0].submittedByName == "Alex"
        assert result[0].submittedByEmail == "alex@test.com"

    async def test_handles_missing_submitter(self, mock_db):
        ex = make_exercise(id="ex-1", is_approved=False, created_by=None)
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_pending_exercises.return_value = [(ex, None)]

            result = await AdminService(mock_db).list_pending_exercises()

        assert result[0].submittedByName is None
        assert result[0].submittedByEmail is None


class TestApproveExercise:
    async def test_success(self, mock_db):
        ex = make_exercise(id="ex-1", is_approved=False)
        approved = make_exercise(id="ex-1", is_approved=True)
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_exercise_by_id.return_value = ex
            repo.approve_exercise.return_value = approved

            result = await AdminService(mock_db).approve_exercise("ex-1")

        assert result.isApproved is True
        repo.approve_exercise.assert_called_once_with(ex)

    async def test_not_found(self, mock_db):
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_exercise_by_id.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await AdminService(mock_db).approve_exercise("missing")

        assert exc_info.value.status_code == 404


class TestRejectExercise:
    async def test_success(self, mock_db):
        ex = make_exercise(id="ex-1")
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_exercise_by_id.return_value = ex

            await AdminService(mock_db).reject_exercise("ex-1")

        repo.delete_exercise.assert_called_once_with(ex)

    async def test_not_found(self, mock_db):
        with patch("app.services.admin.AdminRepository") as MockRepo:
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_exercise_by_id.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await AdminService(mock_db).reject_exercise("missing")

        assert exc_info.value.status_code == 404

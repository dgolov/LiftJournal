from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.admin import AdminRepository
from tests.conftest import make_user, make_exercise, scalar_result, scalars_result


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.delete = AsyncMock()
    return db


@pytest.fixture
def repo(mock_db):
    return AdminRepository(mock_db)


class TestGetAllUsers:
    async def test_returns_list(self, repo, mock_db):
        users = [make_user(id=1), make_user(id=2)]
        mock_db.execute.return_value = scalars_result(users)

        result = await repo.get_all_users()

        assert result == users

    async def test_empty(self, repo, mock_db):
        mock_db.execute.return_value = scalars_result([])

        result = await repo.get_all_users()

        assert result == []


class TestGetPendingExercises:
    async def test_returns_rows_with_submitter(self, repo, mock_db):
        ex = make_exercise(id="ex-1", is_approved=False, created_by=1)
        submitter = make_user(id=1)
        rows_result = MagicMock()
        rows_result.all.return_value = [(ex, submitter)]
        mock_db.execute.return_value = rows_result

        result = await repo.get_pending_exercises()

        assert result == [(ex, submitter)]


class TestGetExerciseById:
    async def test_found(self, repo, mock_db):
        ex = make_exercise(id="ex-1")
        mock_db.execute.return_value = scalar_result(ex)

        result = await repo.get_exercise_by_id("ex-1")

        assert result is ex

    async def test_not_found(self, repo, mock_db):
        mock_db.execute.return_value = scalar_result(None)

        result = await repo.get_exercise_by_id("missing")

        assert result is None


class TestApproveExercise:
    async def test_sets_is_approved_and_commits(self, repo, mock_db):
        ex = make_exercise(id="ex-1", is_approved=False)
        mock_db.refresh = AsyncMock()

        result = await repo.approve_exercise(ex)

        assert ex.is_approved is True
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(ex)
        assert result is ex


class TestDeleteExercise:
    async def test_deletes_and_commits(self, repo, mock_db):
        ex = make_exercise(id="ex-1")

        await repo.delete_exercise(ex)

        mock_db.delete.assert_called_once_with(ex)
        mock_db.commit.assert_called_once()

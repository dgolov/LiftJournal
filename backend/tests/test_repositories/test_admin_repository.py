from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.admin import AdminRepository
from tests.conftest import make_user, make_exercise, make_cycle, scalar_result, scalars_result


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


class TestGetExercises:
    async def test_pending_returns_rows_with_submitter(self, repo, mock_db):
        ex = make_exercise(id="ex-1", status="pending", created_by=1)
        submitter = make_user(id=1)
        rows_result = MagicMock()
        rows_result.all.return_value = [(ex, submitter)]
        mock_db.execute.return_value = rows_result

        result = await repo.get_exercises(status="pending")

        assert result == [(ex, submitter)]

    async def test_all_returns_rows_regardless_of_status(self, repo, mock_db):
        pending = make_exercise(id="ex-1", status="pending")
        approved = make_exercise(id="ex-2", status="approved")
        rejected = make_exercise(id="ex-3", status="rejected")
        rows_result = MagicMock()
        rows_result.all.return_value = [(pending, None), (approved, None), (rejected, None)]
        mock_db.execute.return_value = rows_result

        result = await repo.get_exercises(status="all")

        assert len(result) == 3

    async def test_rejected_status_filters_to_rejected(self, repo, mock_db):
        rejected = make_exercise(id="ex-3", status="rejected")
        rows_result = MagicMock()
        rows_result.all.return_value = [(rejected, None)]
        mock_db.execute.return_value = rows_result

        result = await repo.get_exercises(status="rejected")

        assert result == [(rejected, None)]


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
    async def test_sets_status_approved(self, repo, mock_db):
        ex = make_exercise(id="ex-1", status="pending")
        mock_db.refresh = AsyncMock()

        result = await repo.approve_exercise(ex)

        assert ex.status == "approved"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(ex)
        assert result is ex

    async def test_approves_from_rejected_too(self, repo, mock_db):
        ex = make_exercise(id="ex-1", status="rejected")
        mock_db.refresh = AsyncMock()

        await repo.approve_exercise(ex)

        assert ex.status == "approved"


class TestRevokeExercise:
    async def test_sets_status_private(self, repo, mock_db):
        ex = make_exercise(id="ex-1", status="approved")
        mock_db.refresh = AsyncMock()

        result = await repo.revoke_exercise(ex)

        assert ex.status == "private"
        mock_db.commit.assert_called_once()
        assert result is ex


class TestRejectExercise:
    async def test_sets_status_rejected(self, repo, mock_db):
        ex = make_exercise(id="ex-1", status="pending")
        mock_db.refresh = AsyncMock()

        result = await repo.reject_exercise(ex)

        assert ex.status == "rejected"
        mock_db.commit.assert_called_once()
        assert result is ex


class TestRenameExercise:
    async def test_updates_name_and_commits(self, repo, mock_db):
        ex = make_exercise(id="ex-1", name="Old Name")
        mock_db.refresh = AsyncMock()

        result = await repo.rename_exercise(ex, "New Name")

        assert ex.name == "New Name"
        mock_db.commit.assert_called_once()
        assert result is ex


class TestGetCycles:
    async def test_pending_only_returns_rows_with_counts(self, repo, mock_db):
        c = make_cycle(id="cyc-1", is_public=True, is_approved=False, created_by=1)
        submitter = make_user(id=1)
        rows_mock = MagicMock()
        rows_mock.all.return_value = [(c, submitter)]
        count_row = MagicMock(cycle_id="cyc-1", cnt=3)
        counts_mock = MagicMock()
        counts_mock.__iter__ = MagicMock(return_value=iter([count_row]))
        mock_db.execute.side_effect = [rows_mock, counts_mock]

        rows, counts = await repo.get_cycles(pending_only=True)

        assert rows == [(c, submitter)]
        assert counts == {"cyc-1": 3}

    async def test_all_returns_rows_regardless_of_status(self, repo, mock_db):
        pending = make_cycle(id="cyc-1", is_public=True, is_approved=False)
        approved = make_cycle(id="cyc-2", is_public=True, is_approved=True)
        rows_mock = MagicMock()
        rows_mock.all.return_value = [(pending, None), (approved, None)]
        counts_mock = MagicMock()
        counts_mock.__iter__ = MagicMock(return_value=iter([]))
        mock_db.execute.side_effect = [rows_mock, counts_mock]

        rows, counts = await repo.get_cycles(pending_only=False)

        assert len(rows) == 2
        assert counts == {}


class TestGetCycleById:
    async def test_found(self, repo, mock_db):
        c = make_cycle(id="cyc-1")
        mock_db.execute.return_value = scalar_result(c)

        result = await repo.get_cycle_by_id("cyc-1")

        assert result is c

    async def test_not_found(self, repo, mock_db):
        mock_db.execute.return_value = scalar_result(None)

        result = await repo.get_cycle_by_id("missing")

        assert result is None


class TestApproveCycle:
    async def test_sets_is_approved_and_commits(self, repo, mock_db):
        c = make_cycle(id="cyc-1", is_approved=False)
        mock_db.refresh = AsyncMock()

        result = await repo.approve_cycle(c)

        assert c.is_approved is True
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(c)
        assert result is c


class TestRevokeCycle:
    async def test_sets_not_public_and_unapproved(self, repo, mock_db):
        c = make_cycle(id="cyc-1", is_public=True, is_approved=True)
        mock_db.refresh = AsyncMock()

        result = await repo.revoke_cycle(c)

        assert c.is_public is False
        assert c.is_approved is False
        mock_db.commit.assert_called_once()
        assert result is c


class TestDeleteCycle:
    async def test_deletes_and_commits(self, repo, mock_db):
        c = make_cycle(id="cyc-1")

        await repo.delete_cycle(c)

        mock_db.delete.assert_called_once_with(c)
        mock_db.commit.assert_called_once()

from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.admin import AdminRepository
from tests.conftest import make_user, make_exercise, make_cycle, scalar_result, scalars_result


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
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


class TestGetUserById:
    async def test_found(self, repo, mock_db):
        user = make_user(id=1)
        mock_db.execute.return_value = scalar_result(user)

        result = await repo.get_user_by_id(1)

        assert result == user

    async def test_not_found(self, repo, mock_db):
        mock_db.execute.return_value = scalar_result(None)

        result = await repo.get_user_by_id(999)

        assert result is None


class TestSetUserAdmin:
    async def test_sets_is_admin_and_commits(self, repo, mock_db):
        user = make_user(id=1, is_admin=False)

        result = await repo.set_user_admin(user, True)

        assert result.is_admin is True
        mock_db.commit.assert_awaited_once()
        mock_db.refresh.assert_awaited_once_with(user)

    async def test_revokes_admin(self, repo, mock_db):
        user = make_user(id=1, is_admin=True)

        result = await repo.set_user_admin(user, False)

        assert result.is_admin is False


class TestSetPassword:
    async def test_updates_hashed_password_and_commits(self, repo, mock_db):
        user = make_user(id=1, hashed_password="$2b$12$oldhash")

        await repo.set_password(user, "$2b$12$newhash")

        assert user.hashed_password == "$2b$12$newhash"
        mock_db.commit.assert_awaited_once()


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


class TestCreateExercise:
    async def test_adds_approved_non_custom_exercise(self, repo, mock_db):
        mock_db.refresh = AsyncMock()

        result = await repo.create_exercise(
            name="Zottman Curl", muscle_group="Бицепс", secondary_muscles=["Предплечья"],
            equipment="Гантели", description="Curl variant",
        )

        mock_db.add.assert_called_once()
        added = mock_db.add.call_args[0][0]
        assert added is result
        assert result.name == "Zottman Curl"
        assert result.muscle_group == "Бицепс"
        assert result.secondary_muscles == ["Предплечья"]
        assert result.equipment == "Гантели"
        assert result.description == "Curl variant"
        assert result.is_custom is False
        assert result.status == "approved"
        assert result.created_by is None
        mock_db.commit.assert_called_once()


class TestDeleteExercise:
    async def test_deletes_and_commits(self, repo, mock_db):
        ex = make_exercise(id="ex-1")

        await repo.delete_exercise(ex)

        mock_db.delete.assert_called_once_with(ex)
        mock_db.commit.assert_called_once()


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
    async def test_sets_status_rejected(self, repo, mock_db):
        ex = make_exercise(id="ex-1", status="approved")
        mock_db.refresh = AsyncMock()

        result = await repo.revoke_exercise(ex)

        assert ex.status == "rejected"
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


class TestGetStatsData:
    async def test_returns_counts_and_grouped_rows(self, repo, mock_db):
        mock_db.scalar = AsyncMock(side_effect=[5, 2, 50, 3, 39, 1, 0, 2, 2, 0])

        daily_mock = MagicMock()
        daily_mock.all.return_value = [(date(2026, 8, 15), 3), (date(2026, 8, 17), 1)]

        top_mock = MagicMock()
        top_mock.all.return_value = [(2, 31), (3, 2)]

        user2 = make_user(id=2, name="Дмитрий")
        user3 = make_user(id=3, name="Test")
        users_mock = scalars_result([user2, user3])

        mock_db.execute = AsyncMock(side_effect=[daily_mock, top_mock, users_mock])

        result = await repo.get_stats_data()

        assert result["total_users"] == 5
        assert result["new_users_7d"] == 2
        assert result["total_workouts"] == 50
        assert result["workouts_7d"] == 3
        assert result["total_exercises"] == 39
        assert result["custom_exercises"] == 1
        assert result["pending_exercises"] == 0
        assert result["total_cycles"] == 2
        assert result["public_cycles"] == 2
        assert result["pending_cycles"] == 0
        assert result["daily_rows"] == [(date(2026, 8, 15), 3), (date(2026, 8, 17), 1)]
        assert result["top_rows"] == [(2, 31, "Дмитрий"), (3, 2, "Test")]

    async def test_no_workouts_skips_user_lookup(self, repo, mock_db):
        mock_db.scalar = AsyncMock(side_effect=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        daily_mock = MagicMock()
        daily_mock.all.return_value = []
        top_mock = MagicMock()
        top_mock.all.return_value = []

        mock_db.execute = AsyncMock(side_effect=[daily_mock, top_mock])

        result = await repo.get_stats_data()

        assert result["top_rows"] == []
        assert mock_db.execute.await_count == 2

    async def test_skips_top_row_with_no_matching_user(self, repo, mock_db):
        mock_db.scalar = AsyncMock(side_effect=[1, 0, 1, 0, 0, 0, 0, 0, 0, 0])

        daily_mock = MagicMock()
        daily_mock.all.return_value = []
        top_mock = MagicMock()
        top_mock.all.return_value = [(99, 5)]
        users_mock = scalars_result([])

        mock_db.execute = AsyncMock(side_effect=[daily_mock, top_mock, users_mock])

        result = await repo.get_stats_data()

        assert result["top_rows"] == []

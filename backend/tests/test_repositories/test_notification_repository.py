from unittest.mock import AsyncMock, MagicMock, call

import pytest

from app.repositories.notifications import NotificationRepository
from tests.conftest import scalar_result, scalars_result


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.delete = AsyncMock()
    return db


def _make_notification(id="n-1", user_id=1, type_="like", actor_id=2,
                        workout_id="w-1", is_read=False, comment_text=None):
    n = MagicMock()
    n.id = id
    n.user_id = user_id
    n.type = type_
    n.actor_id = actor_id
    n.workout_id = workout_id
    n.is_read = is_read
    n.comment_text = comment_text
    from datetime import datetime
    n.created_at = datetime(2026, 1, 1, 12, 0)
    return n


class TestCreate:
    async def test_creates_when_no_duplicate(self, mock_db):
        mock_db.execute.return_value = scalar_result(None)

        n = _make_notification()
        mock_db.refresh = AsyncMock()

        repo = NotificationRepository(mock_db)
        # Patch to return a new notification after refresh
        result = await repo.create(user_id=1, type="like", actor_id=2, workout_id="w-1")

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    async def test_deletes_old_duplicate_before_creating(self, mock_db):
        old = _make_notification()
        mock_db.execute.return_value = scalar_result(old)
        mock_db.refresh = AsyncMock()

        repo = NotificationRepository(mock_db)
        await repo.create(user_id=1, type="like", actor_id=2, workout_id="w-1")

        mock_db.delete.assert_called_once_with(old)


class TestGetUnreadCount:
    async def test_returns_count(self, mock_db):
        result_mock = MagicMock()
        result_mock.scalar.return_value = 5
        mock_db.execute.return_value = result_mock

        count = await NotificationRepository(mock_db).get_unread_count(user_id=1)

        assert count == 5

    async def test_returns_zero_when_none(self, mock_db):
        result_mock = MagicMock()
        result_mock.scalar.return_value = None
        mock_db.execute.return_value = result_mock

        count = await NotificationRepository(mock_db).get_unread_count(user_id=1)

        assert count == 0


class TestMarkRead:
    async def test_marks_unread_notification(self, mock_db):
        n = _make_notification(is_read=False)
        mock_db.execute.return_value = scalar_result(n)

        await NotificationRepository(mock_db).mark_read("n-1", user_id=1)

        assert n.is_read is True
        mock_db.commit.assert_called_once()

    async def test_skips_already_read(self, mock_db):
        n = _make_notification(is_read=True)
        mock_db.execute.return_value = scalar_result(n)

        await NotificationRepository(mock_db).mark_read("n-1", user_id=1)

        mock_db.commit.assert_not_called()

    async def test_skips_when_not_found(self, mock_db):
        mock_db.execute.return_value = scalar_result(None)

        await NotificationRepository(mock_db).mark_read("missing", user_id=1)

        mock_db.commit.assert_not_called()


class TestMarkAllRead:
    async def test_marks_all_unread(self, mock_db):
        n1 = _make_notification("n-1", is_read=False)
        n2 = _make_notification("n-2", is_read=False)
        mock_db.execute.return_value = scalars_result([n1, n2])

        await NotificationRepository(mock_db).mark_all_read(user_id=1)

        assert n1.is_read is True
        assert n2.is_read is True
        mock_db.commit.assert_called_once()

    async def test_commits_even_when_none(self, mock_db):
        mock_db.execute.return_value = scalars_result([])

        await NotificationRepository(mock_db).mark_all_read(user_id=1)

        mock_db.commit.assert_called_once()


class TestGetActor:
    async def test_returns_user(self, mock_db):
        from unittest.mock import MagicMock
        user = MagicMock()
        user.id = 2
        mock_db.execute.return_value = scalar_result(user)

        result = await NotificationRepository(mock_db).get_actor(actor_id=2)

        assert result.id == 2

    async def test_returns_none_when_missing(self, mock_db):
        mock_db.execute.return_value = scalar_result(None)

        result = await NotificationRepository(mock_db).get_actor(actor_id=999)

        assert result is None


class TestGetWorkoutTitle:
    async def test_returns_title(self, mock_db):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = "Bench Day"
        mock_db.execute.return_value = result_mock

        title = await NotificationRepository(mock_db).get_workout_title("w-1")

        assert title == "Bench Day"

    async def test_returns_none_when_missing(self, mock_db):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = result_mock

        title = await NotificationRepository(mock_db).get_workout_title("missing")

        assert title is None

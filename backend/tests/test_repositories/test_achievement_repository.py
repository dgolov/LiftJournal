from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.achievements import AchievementRepository
from tests.conftest import scalars_result, scalar_result


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    return db


def _make_ua(user_id=1, achievement_id="first_workout", unlocked_at=None):
    ua = MagicMock()
    ua.user_id = user_id
    ua.achievement_id = achievement_id
    ua.unlocked_at = unlocked_at or datetime(2026, 1, 1)
    return ua


class TestGetForUser:
    async def test_returns_list(self, mock_db):
        ua = _make_ua()
        mock_db.execute.return_value = scalars_result([ua])

        result = await AchievementRepository(mock_db).get_for_user(user_id=1)

        assert result == [ua]
        mock_db.execute.assert_called_once()

    async def test_empty_when_none_unlocked(self, mock_db):
        mock_db.execute.return_value = scalars_result([])

        result = await AchievementRepository(mock_db).get_for_user(user_id=1)

        assert result == []


class TestUnlock:
    async def test_adds_and_commits(self, mock_db):
        repo = AchievementRepository(mock_db)
        now = datetime(2026, 3, 1, 12, 0)

        result = await repo.unlock(user_id=1, achievement_id="streak_3", unlocked_at=now)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        added = mock_db.add.call_args[0][0]
        assert added.user_id == 1
        assert added.achievement_id == "streak_3"
        assert added.unlocked_at == now

    async def test_returns_row(self, mock_db):
        now = datetime(2026, 3, 1)
        result = await AchievementRepository(mock_db).unlock(
            user_id=2, achievement_id="workouts_10", unlocked_at=now
        )
        assert result.achievement_id == "workouts_10"
        assert result.user_id == 2

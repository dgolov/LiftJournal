"""Unit tests for AchievementService and compute_stats."""
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.achievements import (
    AchievementService,
    compute_stats,
    REGISTRY,
    REGISTRY_MAP,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_set(weight=100.0, reps=5, failed=False):
    s = MagicMock()
    s.weight = weight
    s.reps = reps
    s.failed = failed
    return s


def _make_ex(sets):
    ex = MagicMock()
    ex.sets = sets
    return ex


def _make_workout(date_val, volume=1000.0, failed=False):
    """Creates a workout with a single exercise/set yielding the requested volume."""
    s = _make_set(weight=volume, reps=1, failed=failed)
    ex = _make_ex([s])
    w = MagicMock()
    w.date = date_val
    w.exercises = [ex]
    return w


def _workouts_on_consecutive_days(n: int, start: date = date(2026, 1, 1)):
    from datetime import timedelta
    return [_make_workout(start + timedelta(days=i)) for i in range(n)]


# ── compute_stats ─────────────────────────────────────────────────────────────

class TestComputeStats:
    def test_empty(self):
        stats = compute_stats([])
        assert stats["total_workouts"] == 0
        assert stats["total_volume"] == 0.0
        assert stats["max_monthly_volume"] == 0.0
        assert stats["longest_streak"] == 0

    def test_single_workout(self):
        w = _make_workout(date(2026, 1, 10), volume=500.0)
        stats = compute_stats([w])
        assert stats["total_workouts"] == 1
        assert stats["total_volume"] == 500.0
        assert stats["max_monthly_volume"] == 500.0
        assert stats["longest_streak"] == 1

    def test_failed_sets_excluded_from_volume(self):
        s_ok = _make_set(weight=100.0, reps=5, failed=False)
        s_fail = _make_set(weight=200.0, reps=5, failed=True)
        ex = _make_ex([s_ok, s_fail])
        w = MagicMock()
        w.date = date(2026, 1, 1)
        w.exercises = [ex]
        stats = compute_stats([w])
        assert stats["total_volume"] == 500.0  # only s_ok counted

    def test_streak_consecutive(self):
        workouts = _workouts_on_consecutive_days(10)
        stats = compute_stats(workouts)
        assert stats["longest_streak"] == 10

    def test_streak_broken(self):
        from datetime import timedelta
        start = date(2026, 1, 1)
        # 5 days, gap, 3 days
        days = [start + timedelta(days=i) for i in range(5)]
        days += [start + timedelta(days=7 + i) for i in range(3)]
        workouts = [_make_workout(d) for d in days]
        stats = compute_stats(workouts)
        assert stats["longest_streak"] == 5

    def test_streak_multiple_per_day_counts_once(self):
        d = date(2026, 1, 1)
        w1 = _make_workout(d)
        w2 = _make_workout(d)  # same day
        stats = compute_stats([w1, w2])
        assert stats["longest_streak"] == 1

    def test_monthly_volume_max(self):
        jan = _make_workout(date(2026, 1, 1), volume=800.0)
        feb = _make_workout(date(2026, 2, 1), volume=1500.0)
        mar = _make_workout(date(2026, 3, 1), volume=200.0)
        stats = compute_stats([jan, feb, mar])
        assert stats["max_monthly_volume"] == 1500.0
        assert stats["total_volume"] == 2500.0

    def test_total_workouts(self):
        ws = [_make_workout(date(2026, 1, i + 1)) for i in range(7)]
        stats = compute_stats(ws)
        assert stats["total_workouts"] == 7


# ── Achievement conditions ─────────────────────────────────────────────────────

class TestAchievementConditions:
    @pytest.mark.parametrize("aid,key,threshold", [
        ("first_workout",   "total_workouts", 1),
        ("workouts_10",     "total_workouts", 10),
        ("workouts_50",     "total_workouts", 50),
        ("workouts_100",    "total_workouts", 100),
    ])
    def test_count_achievements(self, aid, key, threshold):
        a = REGISTRY_MAP[aid]
        assert not a.check({key: threshold - 1, "longest_streak": 0, "max_monthly_volume": 0, "total_volume": 0})
        assert a.check({key: threshold, "longest_streak": 0, "max_monthly_volume": 0, "total_volume": 0})

    @pytest.mark.parametrize("aid,threshold", [
        ("streak_3",  3),
        ("streak_7",  7),
        ("streak_10", 10),
        ("streak_30", 30),
    ])
    def test_streak_achievements(self, aid, threshold):
        a = REGISTRY_MAP[aid]
        base = {"total_workouts": 100, "total_volume": 0, "max_monthly_volume": 0, "longest_streak": 0}
        assert not a.check({**base, "longest_streak": threshold - 1})
        assert a.check({**base, "longest_streak": threshold})

    @pytest.mark.parametrize("aid,threshold", [
        ("volume_1t_month",  1_000),
        ("volume_10t_month", 10_000),
    ])
    def test_monthly_volume_achievements(self, aid, threshold):
        a = REGISTRY_MAP[aid]
        base = {"total_workouts": 0, "total_volume": 0, "longest_streak": 0, "max_monthly_volume": 0}
        assert not a.check({**base, "max_monthly_volume": threshold - 1})
        assert a.check({**base, "max_monthly_volume": threshold})

    def test_total_volume_achievement(self):
        a = REGISTRY_MAP["volume_100t_total"]
        base = {"total_workouts": 0, "longest_streak": 0, "max_monthly_volume": 0, "total_volume": 0}
        assert not a.check({**base, "total_volume": 99_999})
        assert a.check({**base, "total_volume": 100_000})

    def test_registry_covers_all_ids(self):
        ids = {a.id for a in REGISTRY}
        assert "first_workout" in ids
        assert "streak_10" in ids
        assert "volume_1t_month" in ids
        assert "volume_100t_total" in ids


# ── AchievementService ─────────────────────────────────────────────────────────

@pytest.fixture
def mock_db():
    return AsyncMock()


def _make_unlocked_row(achievement_id: str, unlocked_at=None):
    row = MagicMock()
    row.achievement_id = achievement_id
    row.unlocked_at = unlocked_at or datetime(2026, 1, 1)
    return row


class TestAchievementServiceGetAll:
    async def test_returns_all_achievements(self, mock_db):
        with (
            patch("app.services.achievements.AchievementRepository") as MockRepo,
            patch("app.services.achievements.WorkoutRepository"),
        ):
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_for_user.return_value = []

            result = await AchievementService(mock_db).get_all(user_id=1)

        assert len(result) == len(REGISTRY)

    async def test_unlocked_flag_set_correctly(self, mock_db):
        unlocked = _make_unlocked_row("first_workout")
        with (
            patch("app.services.achievements.AchievementRepository") as MockRepo,
            patch("app.services.achievements.WorkoutRepository"),
        ):
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_for_user.return_value = [unlocked]

            result = await AchievementService(mock_db).get_all(user_id=1)

        by_id = {a.id: a for a in result}
        assert by_id["first_workout"].unlocked is True
        assert by_id["workouts_10"].unlocked is False

    async def test_unlocked_at_populated(self, mock_db):
        ts = datetime(2026, 3, 15, 12, 0)
        unlocked = _make_unlocked_row("streak_10", unlocked_at=ts)
        with (
            patch("app.services.achievements.AchievementRepository") as MockRepo,
            patch("app.services.achievements.WorkoutRepository"),
        ):
            repo = AsyncMock()
            MockRepo.return_value = repo
            repo.get_for_user.return_value = [unlocked]

            result = await AchievementService(mock_db).get_all(user_id=1)

        by_id = {a.id: a for a in result}
        assert by_id["streak_10"].unlockedAt == ts


class TestAchievementServiceEvaluate:
    async def test_unlocks_first_workout(self, mock_db):
        w = _make_workout(date(2026, 1, 1))
        with (
            patch("app.services.achievements.AchievementRepository") as MockRepo,
            patch("app.services.achievements.WorkoutRepository") as MockWRepo,
        ):
            repo = AsyncMock()
            wrepo = AsyncMock()
            MockRepo.return_value = repo
            MockWRepo.return_value = wrepo
            wrepo.get_all_by_user.return_value = [w]
            repo.get_for_user.return_value = []
            repo.unlock = AsyncMock(return_value=MagicMock())

            newly = await AchievementService(mock_db).evaluate(user_id=1)

        unlocked_ids = {a.id for a in newly}
        assert "first_workout" in unlocked_ids

    async def test_does_not_duplicate_already_unlocked(self, mock_db):
        w = _make_workout(date(2026, 1, 1))
        already = _make_unlocked_row("first_workout")
        with (
            patch("app.services.achievements.AchievementRepository") as MockRepo,
            patch("app.services.achievements.WorkoutRepository") as MockWRepo,
        ):
            repo = AsyncMock()
            wrepo = AsyncMock()
            MockRepo.return_value = repo
            MockWRepo.return_value = wrepo
            wrepo.get_all_by_user.return_value = [w]
            repo.get_for_user.return_value = [already]
            repo.unlock = AsyncMock(return_value=MagicMock())

            newly = await AchievementService(mock_db).evaluate(user_id=1)

        unlocked_ids = {a.id for a in newly}
        assert "first_workout" not in unlocked_ids

    async def test_unlocks_streak_10(self, mock_db):
        workouts = _workouts_on_consecutive_days(10)
        with (
            patch("app.services.achievements.AchievementRepository") as MockRepo,
            patch("app.services.achievements.WorkoutRepository") as MockWRepo,
        ):
            repo = AsyncMock()
            wrepo = AsyncMock()
            MockRepo.return_value = repo
            MockWRepo.return_value = wrepo
            wrepo.get_all_by_user.return_value = workouts
            repo.get_for_user.return_value = []
            repo.unlock = AsyncMock(return_value=MagicMock())

            newly = await AchievementService(mock_db).evaluate(user_id=1)

        ids = {a.id for a in newly}
        assert "streak_10" in ids
        assert "streak_7" in ids
        assert "streak_3" in ids
        assert "streak_30" not in ids

    async def test_unlocks_volume_1t_month(self, mock_db):
        w = _make_workout(date(2026, 1, 1), volume=1000.0)
        with (
            patch("app.services.achievements.AchievementRepository") as MockRepo,
            patch("app.services.achievements.WorkoutRepository") as MockWRepo,
        ):
            repo = AsyncMock()
            wrepo = AsyncMock()
            MockRepo.return_value = repo
            MockWRepo.return_value = wrepo
            wrepo.get_all_by_user.return_value = [w]
            repo.get_for_user.return_value = []
            repo.unlock = AsyncMock(return_value=MagicMock())

            newly = await AchievementService(mock_db).evaluate(user_id=1)

        ids = {a.id for a in newly}
        assert "volume_1t_month" in ids

    async def test_returns_empty_when_no_new_achievements(self, mock_db):
        with (
            patch("app.services.achievements.AchievementRepository") as MockRepo,
            patch("app.services.achievements.WorkoutRepository") as MockWRepo,
        ):
            repo = AsyncMock()
            wrepo = AsyncMock()
            MockRepo.return_value = repo
            MockWRepo.return_value = wrepo
            wrepo.get_all_by_user.return_value = []
            repo.get_for_user.return_value = []
            repo.unlock = AsyncMock(return_value=MagicMock())

            newly = await AchievementService(mock_db).evaluate(user_id=1)

        assert newly == []

    async def test_persist_called_for_each_new_achievement(self, mock_db):
        workouts = _workouts_on_consecutive_days(3)
        with (
            patch("app.services.achievements.AchievementRepository") as MockRepo,
            patch("app.services.achievements.WorkoutRepository") as MockWRepo,
        ):
            repo = AsyncMock()
            wrepo = AsyncMock()
            MockRepo.return_value = repo
            MockWRepo.return_value = wrepo
            wrepo.get_all_by_user.return_value = workouts
            repo.get_for_user.return_value = []
            repo.unlock = AsyncMock(return_value=MagicMock())

            newly = await AchievementService(mock_db).evaluate(user_id=1)

        # At least streak_3, first_workout, workouts_10 (3 workouts < 10, so only first_workout+streak_3)
        assert repo.unlock.call_count == len(newly)

from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.achievements import AchievementRepository
from app.repositories.workout import WorkoutRepository
from app.api.schemas import AchievementOut


# ── Achievement registry ───────────────────────────────────────────────────────

@dataclass(frozen=True)
class AchievementDef:
    id: str
    title: str
    description: str
    icon: str
    category: str  # count | streak | volume_month | volume_total | strength_max
    check: Callable[[dict], bool]


def _count(n: int) -> Callable[[dict], bool]:
    return lambda s: s["total_workouts"] >= n

def _streak(n: int) -> Callable[[dict], bool]:
    return lambda s: s["longest_streak"] >= n

def _vol_month(n: float) -> Callable[[dict], bool]:
    return lambda s: s["max_monthly_volume"] >= n

def _vol_total(n: float) -> Callable[[dict], bool]:
    return lambda s: s["total_volume"] >= n

def _max_weight(exercise_id: str, n: float) -> Callable[[dict], bool]:
    return lambda s: s["max_weight_by_exercise"].get(exercise_id, 0.0) >= n


REGISTRY: list[AchievementDef] = [
    # ── Количество тренировок ──────────────────────────────────────────────────
    AchievementDef("first_workout",   "Первый шаг",          "Запишите первую тренировку",      "🎯", "count",        _count(1)),
    AchievementDef("workouts_10",     "Начало пути",          "Завершите 10 тренировок",         "🥉", "count",        _count(10)),
    AchievementDef("workouts_50",     "Полтинник",            "Завершите 50 тренировок",         "🥈", "count",        _count(50)),
    AchievementDef("workouts_100",    "Сотня",                "Завершите 100 тренировок",        "🥇", "count",        _count(100)),
    # ── Стрик ─────────────────────────────────────────────────────────────────
    AchievementDef("streak_3",        "Первая серия",         "3 тренировки подряд",             "🔥", "streak",       _streak(3)),
    AchievementDef("streak_7",        "Неделя без пропусков", "7 тренировок подряд",             "💪", "streak",       _streak(7)),
    AchievementDef("streak_10",       "На огне",              "10 тренировок подряд",            "🔥", "streak",       _streak(10)),
    AchievementDef("streak_30",       "Железная воля",        "30 тренировок подряд",            "🏆", "streak",       _streak(30)),
    # ── Тоннаж за месяц ───────────────────────────────────────────────────────
    AchievementDef("volume_1t_month", "Первая тонна",         "1 000 кг тоннажа за один месяц", "💣", "volume_month", _vol_month(1_000)),
    AchievementDef("volume_10t_month","Десять тонн",          "10 000 кг за один месяц",        "🏋️", "volume_month", _vol_month(10_000)),
    # ── Суммарный тоннаж ──────────────────────────────────────────────────────
    AchievementDef("volume_100t_total","Сотня тонн",          "100 000 кг суммарно",            "🌐", "volume_total", _vol_total(100_000)),
    # ── Силовые клубы ─────────────────────────────────────────────────────────
    AchievementDef("bench_club_100",    "Клуб 100 (жим лёжа)",    "Пожмите 100 кг в жиме лёжа",     "🏋️‍♂️", "strength_max", _max_weight("ex-001", 100)),
    AchievementDef("bench_club_200",    "Клуб 200 (жим лёжа)",    "Пожмите 200 кг в жиме лёжа",     "👑", "strength_max", _max_weight("ex-001", 200)),
    AchievementDef("deadlift_club_200", "Клуб 200 (становая тяга)", "Потяните 200 кг в становой тяге", "🏋️", "strength_max", _max_weight("ex-006", 200)),
    AchievementDef("deadlift_club_300", "Клуб 300 (становая тяга)", "Потяните 300 кг в становой тяге", "👑", "strength_max", _max_weight("ex-006", 300)),
    AchievementDef("squat_club_200",    "Клуб 200 (присед)",        "Присядьте с 200 кг",              "🦵", "strength_max", _max_weight("ex-024", 200)),
    AchievementDef("squat_club_300",    "Клуб 300 (присед)",        "Присядьте с 300 кг",              "👑", "strength_max", _max_weight("ex-024", 300)),
]

REGISTRY_MAP: dict[str, AchievementDef] = {a.id: a for a in REGISTRY}


# ── Stats computation (pure, no DB) ───────────────────────────────────────────

def compute_stats(workouts: list) -> dict:
    """Compute achievement-relevant stats from a list of ORM Workout objects."""
    total = len(workouts)

    def workout_volume(w) -> float:
        v = 0.0
        for ex in w.exercises:
            for s in ex.sets:
                if not getattr(s, "failed", False):
                    v += (s.weight or 0.0) * (s.reps or 0)
        return v

    total_volume = sum(workout_volume(w) for w in workouts)

    monthly: dict[str, float] = {}
    for w in workouts:
        key = w.date.strftime("%Y-%m")
        monthly[key] = monthly.get(key, 0.0) + workout_volume(w)
    max_monthly = max(monthly.values(), default=0.0)

    dates = sorted({w.date for w in workouts})
    longest = 0
    current = 0
    for i, d in enumerate(dates):
        if i == 0:
            current = 1
        else:
            delta = (d - dates[i - 1]).days
            current = current + 1 if delta == 1 else 1
        longest = max(longest, current)

    max_weight_by_exercise: dict[str, float] = {}
    for w in workouts:
        for ex in w.exercises:
            for s in ex.sets:
                if getattr(s, "failed", False):
                    continue
                weight = s.weight or 0.0
                if weight > max_weight_by_exercise.get(ex.exercise_id, 0.0):
                    max_weight_by_exercise[ex.exercise_id] = weight

    return {
        "total_workouts": total,
        "total_volume": total_volume,
        "max_monthly_volume": max_monthly,
        "longest_streak": longest,
        "max_weight_by_exercise": max_weight_by_exercise,
    }


# ── Service ────────────────────────────────────────────────────────────────────

class AchievementService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = AchievementRepository(db)
        self.workout_repo = WorkoutRepository(db)

    async def get_all(self, user_id: int) -> list[AchievementOut]:
        """Return all achievements, marking which are unlocked."""
        unlocked = {a.achievement_id: a.unlocked_at for a in await self.repo.get_for_user(user_id)}
        return [
            AchievementOut(
                id=a.id,
                title=a.title,
                description=a.description,
                icon=a.icon,
                category=a.category,
                unlocked=a.id in unlocked,
                unlockedAt=unlocked.get(a.id),
            )
            for a in REGISTRY
        ]

    async def evaluate(self, user_id: int) -> list[AchievementOut]:
        """Check all achievements, persist newly unlocked ones, return them."""
        workouts = await self.workout_repo.get_all_by_user(user_id)
        stats = compute_stats(workouts)
        already = {a.achievement_id for a in await self.repo.get_for_user(user_id)}
        newly_unlocked: list[AchievementOut] = []
        now = datetime.utcnow()
        for a in REGISTRY:
            if a.id not in already and a.check(stats):
                await self.repo.unlock(user_id=user_id, achievement_id=a.id, unlocked_at=now)
                newly_unlocked.append(
                    AchievementOut(
                        id=a.id, title=a.title, description=a.description,
                        icon=a.icon, category=a.category,
                        unlocked=True, unlockedAt=now,
                    )
                )
        return newly_unlocked

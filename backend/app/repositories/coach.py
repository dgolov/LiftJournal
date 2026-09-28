from datetime import date, datetime

from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import CoachAthlete, User, UserFollow, Workout, PlannedWorkout, WeightEntry

OPEN_STATUSES = ("pending", "active")


class CoachRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_user(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def is_following(self, follower_id: int, following_id: int) -> bool:
        result = await self.db.execute(
            select(UserFollow.id).where(
                UserFollow.follower_id == follower_id,
                UserFollow.following_id == following_id,
            )
        )
        return result.scalar_one_or_none() is not None

    # ── Links ────────────────────────────────────────────────────────────────

    async def get_link(self, link_id: str) -> CoachAthlete | None:
        result = await self.db.execute(select(CoachAthlete).where(CoachAthlete.id == link_id))
        return result.scalar_one_or_none()

    async def get_open_link(self, coach_id: int, athlete_id: int) -> CoachAthlete | None:
        result = await self.db.execute(
            select(CoachAthlete).where(
                CoachAthlete.coach_id == coach_id,
                CoachAthlete.athlete_id == athlete_id,
                CoachAthlete.status.in_(OPEN_STATUSES),
            )
        )
        return result.scalar_one_or_none()

    async def get_active_link(self, coach_id: int, athlete_id: int) -> CoachAthlete | None:
        result = await self.db.execute(
            select(CoachAthlete).where(
                CoachAthlete.coach_id == coach_id,
                CoachAthlete.athlete_id == athlete_id,
                CoachAthlete.status == "active",
            )
        )
        return result.scalar_one_or_none()

    async def get_open_link_between(self, user_a: int, user_b: int) -> CoachAthlete | None:
        """The open link between two users, whichever of them is the coach."""
        result = await self.db.execute(
            select(CoachAthlete)
            .where(
                CoachAthlete.status.in_(OPEN_STATUSES),
                or_(
                    and_(CoachAthlete.coach_id == user_a, CoachAthlete.athlete_id == user_b),
                    and_(CoachAthlete.coach_id == user_b, CoachAthlete.athlete_id == user_a),
                ),
            )
            .order_by(CoachAthlete.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create_link(
        self, *, coach_id: int, athlete_id: int, initiated_by: str, message: str,
    ) -> CoachAthlete:
        link = CoachAthlete(
            coach_id=coach_id,
            athlete_id=athlete_id,
            status="pending",
            initiated_by=initiated_by,
            message=message,
            can_see_private=True,
            can_edit_plan=True,
            created_at=datetime.utcnow(),
        )
        self.db.add(link)
        await self.db.commit()
        await self.db.refresh(link)
        return link

    async def save(self, link: CoachAthlete) -> CoachAthlete:
        await self.db.commit()
        await self.db.refresh(link)
        return link

    async def delete(self, link: CoachAthlete) -> None:
        await self.db.delete(link)
        await self.db.commit()

    async def list_links(
        self, user_id: int, role: str | None = None, statuses: list[str] | None = None,
    ) -> list[tuple[CoachAthlete, User, User]]:
        """(link, coach, athlete) rows where the user is on the given side."""
        Coach = aliased(User)
        Athlete = aliased(User)
        q = (
            select(CoachAthlete, Coach, Athlete)
            .join(Coach, Coach.id == CoachAthlete.coach_id)
            .join(Athlete, Athlete.id == CoachAthlete.athlete_id)
        )
        if role == "coach":
            q = q.where(CoachAthlete.coach_id == user_id)
        elif role == "athlete":
            q = q.where(CoachAthlete.athlete_id == user_id)
        else:
            q = q.where(or_(CoachAthlete.coach_id == user_id, CoachAthlete.athlete_id == user_id))
        if statuses:
            q = q.where(CoachAthlete.status.in_(statuses))
        result = await self.db.execute(q.order_by(CoachAthlete.created_at.desc()))
        return [tuple(row) for row in result.all()]

    async def count_active_athletes(self, coach_id: int) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(CoachAthlete)
            .where(CoachAthlete.coach_id == coach_id, CoachAthlete.status == "active")
        )
        return result.scalar() or 0

    # ── Athlete data ─────────────────────────────────────────────────────────

    async def last_workout_date(self, athlete_id: int) -> date | None:
        result = await self.db.execute(
            select(func.max(Workout.date)).where(Workout.user_id == athlete_id)
        )
        return result.scalar()

    async def count_workouts(self, athlete_id: int, date_from: date, date_to: date) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Workout).where(
                Workout.user_id == athlete_id,
                Workout.date >= date_from,
                Workout.date <= date_to,
            )
        )
        return result.scalar() or 0

    async def count_planned(self, athlete_id: int, date_from: date, date_to: date) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(PlannedWorkout).where(
                PlannedWorkout.user_id == athlete_id,
                PlannedWorkout.scheduled_date >= date_from,
                PlannedWorkout.scheduled_date <= date_to,
            )
        )
        return result.scalar() or 0

    async def get_weight_log(self, athlete_id: int) -> list[WeightEntry]:
        result = await self.db.execute(
            select(WeightEntry).where(WeightEntry.user_id == athlete_id).order_by(WeightEntry.date)
        )
        return list(result.scalars().all())

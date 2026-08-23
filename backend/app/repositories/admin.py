from datetime import datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import User, Exercise, TrainingCycle, CycleWorkout, Workout


class AdminRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all_users(self) -> list[User]:
        result = await self.db.execute(select(User).order_by(User.id))
        return list(result.scalars().all())

    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def set_user_admin(self, user: User, is_admin: bool) -> User:
        user.is_admin = is_admin
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_exercises(
        self, *, status: str = "pending", search: str | None = None, muscle_group: str | None = None
    ):
        """Each row is (Exercise, submitting User | None) — an outer join since
        created_by is nullable (built-in exercises have no submitter)."""
        query = select(Exercise, User).outerjoin(User, Exercise.created_by == User.id)
        if status != "all":
            query = query.where(Exercise.status == status)
        if search:
            query = query.where(Exercise.name.ilike(f"%{search}%"))
        if muscle_group:
            query = query.where(Exercise.muscle_group == muscle_group)
        result = await self.db.execute(query.order_by(Exercise.name))
        return result.all()

    async def get_exercise_by_id(self, exercise_id: str) -> Exercise | None:
        result = await self.db.execute(select(Exercise).where(Exercise.id == exercise_id))
        return result.scalar_one_or_none()

    async def approve_exercise(self, exercise: Exercise) -> Exercise:
        exercise.status = "approved"
        await self.db.commit()
        await self.db.refresh(exercise)
        return exercise

    async def revoke_exercise(self, exercise: Exercise) -> Exercise:
        exercise.status = "private"
        await self.db.commit()
        await self.db.refresh(exercise)
        return exercise

    async def reject_exercise(self, exercise: Exercise) -> Exercise:
        exercise.status = "rejected"
        await self.db.commit()
        await self.db.refresh(exercise)
        return exercise

    async def rename_exercise(self, exercise: Exercise, name: str) -> Exercise:
        exercise.name = name
        await self.db.commit()
        await self.db.refresh(exercise)
        return exercise

    async def get_cycles(self, *, pending_only: bool):
        """Each row is (TrainingCycle, submitting User | None). Workout counts
        come back separately, mirroring CycleRepository.get_all_visible."""
        query = select(TrainingCycle, User).outerjoin(User, TrainingCycle.created_by == User.id)
        if pending_only:
            query = query.where(
                (TrainingCycle.is_public.is_(True)) & (TrainingCycle.is_approved.is_(False))
            )
        result = await self.db.execute(query.order_by(TrainingCycle.created_at.desc()))
        rows = result.all()

        count_result = await self.db.execute(
            select(CycleWorkout.cycle_id, func.count(CycleWorkout.id).label("cnt"))
            .group_by(CycleWorkout.cycle_id)
        )
        counts = {row.cycle_id: row.cnt for row in count_result}
        return rows, counts

    async def get_cycle_by_id(self, cycle_id: str) -> TrainingCycle | None:
        result = await self.db.execute(select(TrainingCycle).where(TrainingCycle.id == cycle_id))
        return result.scalar_one_or_none()

    async def approve_cycle(self, cycle: TrainingCycle) -> TrainingCycle:
        cycle.is_approved = True
        await self.db.commit()
        await self.db.refresh(cycle)
        return cycle

    async def revoke_cycle(self, cycle: TrainingCycle) -> TrainingCycle:
        cycle.is_public = False
        cycle.is_approved = False
        await self.db.commit()
        await self.db.refresh(cycle)
        return cycle

    async def delete_cycle(self, cycle: TrainingCycle) -> None:
        await self.db.delete(cycle)
        await self.db.commit()

    async def get_stats_data(self) -> dict:
        """Raw counts and grouped rows for the dashboard — date-filling and
        DTO shaping happen in the service, this just runs the queries."""
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        two_weeks_ago = now - timedelta(days=14)

        total_users = await self.db.scalar(select(func.count()).select_from(User))
        new_users_7d = await self.db.scalar(
            select(func.count()).select_from(User).where(User.created_at >= week_ago)
        )
        total_workouts = await self.db.scalar(select(func.count()).select_from(Workout))
        workouts_7d = await self.db.scalar(
            select(func.count()).select_from(Workout).where(Workout.created_at >= week_ago)
        )
        total_exercises = await self.db.scalar(select(func.count()).select_from(Exercise))
        custom_exercises = await self.db.scalar(
            select(func.count()).select_from(Exercise).where(Exercise.is_custom.is_(True))
        )
        pending_exercises = await self.db.scalar(
            select(func.count()).select_from(Exercise).where(Exercise.status == "pending")
        )
        total_cycles = await self.db.scalar(select(func.count()).select_from(TrainingCycle))
        public_cycles = await self.db.scalar(
            select(func.count()).select_from(TrainingCycle)
            .where(TrainingCycle.is_public.is_(True), TrainingCycle.is_approved.is_(True))
        )
        pending_cycles = await self.db.scalar(
            select(func.count()).select_from(TrainingCycle)
            .where(TrainingCycle.is_public.is_(True), TrainingCycle.is_approved.is_(False))
        )

        daily_result = await self.db.execute(
            select(func.date(Workout.created_at), func.count())
            .where(Workout.created_at >= two_weeks_ago)
            .group_by(func.date(Workout.created_at))
        )
        daily_rows = daily_result.all()

        top_result = await self.db.execute(
            select(Workout.user_id, func.count().label("cnt"))
            .where(Workout.user_id.is_not(None))
            .group_by(Workout.user_id)
            .order_by(func.count().desc())
            .limit(5)
        )
        top_rows = top_result.all()
        top_user_ids = [uid for uid, _ in top_rows]
        users_by_id = {}
        if top_user_ids:
            users_result = await self.db.execute(select(User).where(User.id.in_(top_user_ids)))
            users_by_id = {u.id: u for u in users_result.scalars().all()}

        return {
            "total_users": total_users,
            "new_users_7d": new_users_7d,
            "total_workouts": total_workouts,
            "workouts_7d": workouts_7d,
            "total_exercises": total_exercises,
            "custom_exercises": custom_exercises,
            "pending_exercises": pending_exercises,
            "total_cycles": total_cycles,
            "public_cycles": public_cycles,
            "pending_cycles": pending_cycles,
            "daily_rows": daily_rows,
            "top_rows": [(uid, cnt, users_by_id[uid].name) for uid, cnt in top_rows if uid in users_by_id],
        }

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import User, Exercise, TrainingCycle, CycleWorkout


class AdminRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all_users(self) -> list[User]:
        result = await self.db.execute(select(User).order_by(User.id))
        return list(result.scalars().all())

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

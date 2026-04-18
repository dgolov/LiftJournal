from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import PlannedWorkout, PlannedExercise, PlannedSet


class PlannedWorkoutRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _eager(self):
        return selectinload(PlannedWorkout.exercises).selectinload(PlannedExercise.sets)

    async def get_all_by_user(self, user_id: int) -> list[PlannedWorkout]:
        result = await self.db.execute(
            select(PlannedWorkout)
            .options(self._eager())
            .where(PlannedWorkout.user_id == user_id)
            .order_by(PlannedWorkout.scheduled_date.asc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, plan_id: str) -> PlannedWorkout | None:
        result = await self.db.execute(
            select(PlannedWorkout).options(self._eager()).where(PlannedWorkout.id == plan_id)
        )
        return result.scalar_one_or_none()

    async def create(self, *, user_id: int, title: str, type: str, scheduled_date, notes: str, exercises_data: list) -> PlannedWorkout:
        plan = PlannedWorkout(
            user_id=user_id,
            title=title,
            type=type,
            scheduled_date=scheduled_date,
            notes=notes,
            status="planned",
            created_at=datetime.utcnow(),
        )
        plan.exercises = self._build_exercises(exercises_data)
        self.db.add(plan)
        await self.db.commit()
        return await self.get_by_id(plan.id)  # type: ignore[return-value]

    async def update(self, plan: PlannedWorkout, *, title=None, type=None, scheduled_date=None, notes=None, status=None, completed_workout_id=None, exercises_data=None) -> PlannedWorkout:
        if title is not None:
            plan.title = title
        if type is not None:
            plan.type = type
        if scheduled_date is not None:
            plan.scheduled_date = scheduled_date
        if notes is not None:
            plan.notes = notes
        if status is not None:
            plan.status = status
        if completed_workout_id is not None:
            plan.completed_workout_id = completed_workout_id
        if exercises_data is not None:
            plan.exercises = self._build_exercises(exercises_data)
        await self.db.commit()
        return await self.get_by_id(plan.id)  # type: ignore[return-value]

    async def delete(self, plan: PlannedWorkout) -> None:
        await self.db.delete(plan)
        await self.db.commit()

    def _build_exercises(self, exercises_data: list) -> list[PlannedExercise]:
        result = []
        for i, ex in enumerate(exercises_data):
            pe = PlannedExercise(
                exercise_id=ex.exerciseId,
                exercise_name=ex.exerciseName,
                order=i,
            )
            pe.sets = [
                PlannedSet(weight=s.weight, reps=s.reps, order=j)
                for j, s in enumerate(ex.sets)
            ]
            result.append(pe)
        return result

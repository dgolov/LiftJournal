from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import Workout, WorkoutExercise, ExerciseSet


class WorkoutRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _eager(self):
        return selectinload(Workout.exercises).selectinload(WorkoutExercise.sets)

    async def get_all_by_user(self, user_id: int) -> list[Workout]:
        result = await self.db.execute(
            select(Workout)
            .options(self._eager())
            .where(Workout.user_id == user_id)
            .order_by(Workout.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, workout_id: str) -> Workout | None:
        result = await self.db.execute(
            select(Workout).options(self._eager()).where(Workout.id == workout_id)
        )
        return result.scalar_one_or_none()

    async def create(self, *, user_id: int, date, type: str, title: str, duration_minutes: int, notes: str, exercises_data: list) -> Workout:
        workout = Workout(
            user_id=user_id,
            date=date,
            type=type,
            title=title,
            duration_minutes=duration_minutes,
            notes=notes,
            created_at=datetime.utcnow(),
        )
        workout.exercises = self._build_exercises(exercises_data)
        self.db.add(workout)
        await self.db.commit()
        return await self.get_by_id(workout.id)  # type: ignore[return-value]

    async def update(
        self,
        workout: Workout,
        *,
        date=None,
        type: str | None = None,
        title: str | None = None,
        duration_minutes: int | None = None,
        notes: str | None = None,
        exercises_data: list | None = None,
    ) -> Workout:
        if date is not None:
            workout.date = date
        if type is not None:
            workout.type = type
        if title is not None:
            workout.title = title
        if duration_minutes is not None:
            workout.duration_minutes = duration_minutes
        if notes is not None:
            workout.notes = notes
        if exercises_data is not None:
            workout.exercises = self._build_exercises(exercises_data)
        await self.db.commit()
        return await self.get_by_id(workout.id)  # type: ignore[return-value]

    async def delete(self, workout: Workout) -> None:
        await self.db.delete(workout)
        await self.db.commit()

    def _build_exercises(self, exercises_data: list) -> list[WorkoutExercise]:
        result = []
        for i, ex in enumerate(exercises_data):
            we = WorkoutExercise(
                exercise_id=ex.exerciseId,
                exercise_name=ex.exerciseName,
                order=i,
            )
            we.sets = [
                ExerciseSet(weight=s.weight, reps=s.reps, completed=s.completed, order=j)
                for j, s in enumerate(ex.sets)
            ]
            result.append(we)
        return result

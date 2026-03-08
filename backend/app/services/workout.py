from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import WorkoutCreate, WorkoutUpdate, WorkoutOut, WorkoutExerciseOut, SetOut
from app.repositories.workout import WorkoutRepository
from app.domain.models import Workout


class WorkoutService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = WorkoutRepository(db)

    def _to_dto(self, w: Workout) -> WorkoutOut:
        return WorkoutOut(
            id=w.id,
            date=w.date,
            type=w.type,
            title=w.title,
            durationMinutes=w.duration_minutes,
            notes=w.notes or "",
            createdAt=w.created_at,
            exercises=[
                WorkoutExerciseOut(
                    exerciseId=ex.exercise_id,
                    exerciseName=ex.exercise_name,
                    sets=[
                        SetOut(id=s.id, weight=s.weight, reps=s.reps, completed=s.completed)
                        for s in ex.sets
                    ],
                )
                for ex in w.exercises
            ],
        )

    async def get_workouts(self, user_id: int) -> list[WorkoutOut]:
        return [self._to_dto(w) for w in await self.repo.get_all_by_user(user_id)]

    async def get_workout(self, workout_id: str, user_id: int) -> WorkoutOut:
        w = await self.repo.get_by_id(workout_id)
        if not w:
            raise HTTPException(status_code=404, detail="Workout not found")
        if w.user_id != user_id:
            raise HTTPException(status_code=403, detail="Нет доступа")
        return self._to_dto(w)

    async def create_workout(self, data: WorkoutCreate, user_id: int) -> WorkoutOut:
        w = await self.repo.create(
            user_id=user_id,
            date=data.date,
            type=data.type,
            title=data.title,
            duration_minutes=data.durationMinutes,
            notes=data.notes,
            exercises_data=data.exercises,
        )
        return self._to_dto(w)

    async def update_workout(self, workout_id: str, data: WorkoutUpdate, user_id: int) -> WorkoutOut:
        w = await self.repo.get_by_id(workout_id)
        if not w:
            raise HTTPException(status_code=404, detail="Workout not found")
        if w.user_id != user_id:
            raise HTTPException(status_code=403, detail="Нет доступа")
        w = await self.repo.update(
            w,
            date=data.date,
            type=data.type,
            title=data.title,
            duration_minutes=data.durationMinutes,
            notes=data.notes,
            exercises_data=data.exercises,
        )
        return self._to_dto(w)

    async def delete_workout(self, workout_id: str, user_id: int) -> None:
        w = await self.repo.get_by_id(workout_id)
        if not w:
            raise HTTPException(status_code=404, detail="Workout not found")
        if w.user_id != user_id:
            raise HTTPException(status_code=403, detail="Нет доступа")
        await self.repo.delete(w)

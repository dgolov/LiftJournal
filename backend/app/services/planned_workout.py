from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    PlannedWorkoutCreate, PlannedWorkoutUpdate, PlannedWorkoutOut,
    PlannedExerciseOut, PlannedSetOut,
)
from app.domain.models import PlannedWorkout
from app.repositories.planned_workout import PlannedWorkoutRepository


class PlannedWorkoutService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = PlannedWorkoutRepository(db)

    def _to_dto(self, p: PlannedWorkout) -> PlannedWorkoutOut:
        return PlannedWorkoutOut(
            id=p.id,
            title=p.title,
            type=p.type,
            scheduledDate=p.scheduled_date,
            notes=p.notes or "",
            status=p.status,
            completedWorkoutId=p.completed_workout_id,
            createdAt=p.created_at,
            exercises=[
                PlannedExerciseOut(
                    exerciseId=ex.exercise_id,
                    exerciseName=ex.exercise_name,
                    sets=[
                        PlannedSetOut(id=s.id, weight=s.weight, reps=s.reps)
                        for s in ex.sets
                    ],
                )
                for ex in p.exercises
            ],
        )

    async def get_all(self, user_id: int) -> list[PlannedWorkoutOut]:
        return [self._to_dto(p) for p in await self.repo.get_all_by_user(user_id)]

    async def get_one(self, plan_id: str, user_id: int) -> PlannedWorkoutOut:
        p = await self.repo.get_by_id(plan_id)
        if not p:
            raise HTTPException(status_code=404, detail="Planned workout not found")
        if p.user_id != user_id:
            raise HTTPException(status_code=403, detail="Нет доступа")
        return self._to_dto(p)

    async def create(self, data: PlannedWorkoutCreate, user_id: int) -> PlannedWorkoutOut:
        p = await self.repo.create(
            user_id=user_id,
            title=data.title,
            type=data.type,
            scheduled_date=data.scheduledDate,
            notes=data.notes,
            exercises_data=data.exercises,
        )
        return self._to_dto(p)

    async def update(self, plan_id: str, data: PlannedWorkoutUpdate, user_id: int) -> PlannedWorkoutOut:
        p = await self.repo.get_by_id(plan_id)
        if not p:
            raise HTTPException(status_code=404, detail="Planned workout not found")
        if p.user_id != user_id:
            raise HTTPException(status_code=403, detail="Нет доступа")
        p = await self.repo.update(
            p,
            title=data.title,
            type=data.type,
            scheduled_date=data.scheduledDate,
            notes=data.notes,
            status=data.status,
            completed_workout_id=data.completedWorkoutId,
            exercises_data=data.exercises,
        )
        return self._to_dto(p)

    async def delete(self, plan_id: str, user_id: int) -> None:
        p = await self.repo.get_by_id(plan_id)
        if not p:
            raise HTTPException(status_code=404, detail="Planned workout not found")
        if p.user_id != user_id:
            raise HTTPException(status_code=403, detail="Нет доступа")
        await self.repo.delete(p)

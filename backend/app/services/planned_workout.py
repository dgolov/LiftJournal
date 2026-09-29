from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    PlannedWorkoutCreate, PlannedWorkoutUpdate, PlannedWorkoutOut,
    PlannedExerciseOut, PlannedSetOut, CycleMainExercise,
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
            createdById=p.created_by if p.created_by and p.created_by != p.user_id else None,
            createdByName=p.creator.name if p.created_by and p.created_by != p.user_id and p.creator else None,
            cycleId=p.cycle_id,
            cycleScheduleId=p.cycle_schedule_id,
            cycleTitle=p.cycle.title if p.cycle_id and p.cycle else None,
            cycleMainExercises=[CycleMainExercise(**m) for m in (p.cycle.main_exercises or [])] if p.cycle_id and p.cycle else [],
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

    async def check_cycle(self, cycle_id: str | None, planner_id: int) -> None:
        """A plan may point at a cycle only if whoever lays it out can see that
        cycle — otherwise it would leak a private cycle's title and lifts."""
        if not cycle_id:
            return
        from app.repositories.cycle import CycleRepository
        from app.services.cycle import can_see_cycle
        cycle = await CycleRepository(self.repo.db).get_by_id(cycle_id)
        if not cycle or not can_see_cycle(cycle, planner_id):
            raise HTTPException(status_code=404, detail="Цикл не найден")

    async def create(self, data: PlannedWorkoutCreate, user_id: int) -> PlannedWorkoutOut:
        await self.check_cycle(data.cycleId, user_id)
        p = await self.repo.create(
            user_id=user_id,
            cycle_id=data.cycleId,
            cycle_schedule_id=data.cycleScheduleId,
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
        was_completed = p.status == "completed"
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
        if not was_completed and p.status == "completed":
            await self._notify_coach_completed(p)
        return self._to_dto(p)

    async def _notify_coach_completed(self, p: PlannedWorkout) -> None:
        """Tell the coach who wrote this plan that the athlete did it — but only
        while they still coach them."""
        if not p.created_by or p.created_by == p.user_id:
            return
        from app.repositories.coach import CoachRepository
        if not await CoachRepository(self.repo.db).get_active_link(p.created_by, p.user_id):
            return
        from app.services.notifications import NotificationService
        await NotificationService(self.repo.db).notify_athlete_completed(
            athlete_id=p.user_id, coach_id=p.created_by,
            planned_workout_id=p.id, workout_id=p.completed_workout_id,
        )

    async def delete(self, plan_id: str, user_id: int) -> None:
        p = await self.repo.get_by_id(plan_id)
        if not p:
            raise HTTPException(status_code=404, detail="Planned workout not found")
        if p.user_id != user_id:
            raise HTTPException(status_code=403, detail="Нет доступа")
        await self.repo.delete(p)

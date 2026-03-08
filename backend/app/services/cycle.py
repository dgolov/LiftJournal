from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    CycleCreate, CycleUpdate, CycleListOut, CycleDetailOut,
    CycleWorkoutOut, CycleExerciseOut, CycleSetOut,
)
from app.repositories.cycle import CycleRepository
from app.domain.models import TrainingCycle


class CycleService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = CycleRepository(db)

    def _to_detail(self, c: TrainingCycle) -> CycleDetailOut:
        return CycleDetailOut(
            id=c.id,
            title=c.title,
            description=c.description or "",
            author_name=c.author_name or "",
            created_by=c.created_by,
            is_public=c.is_public,
            created_at=c.created_at,
            workouts=[
                CycleWorkoutOut(
                    id=w.id,
                    workout_number=w.workout_number,
                    title=w.title or "",
                    notes=w.notes or "",
                    exercises=[
                        CycleExerciseOut(
                            id=e.id,
                            exercise_id=e.exercise_id,
                            exercise_name=e.exercise_name,
                            sets=[
                                CycleSetOut(id=s.id, percent_1rm=s.percent_1rm, reps=s.reps, order=s.order)
                                for s in e.sets
                            ],
                        )
                        for e in w.exercises
                    ],
                )
                for w in c.workouts
            ],
        )

    async def list_cycles(self, user_id: int) -> list[CycleListOut]:
        cycles, counts = await self.repo.get_all_visible(user_id)
        return [
            CycleListOut(
                id=c.id,
                title=c.title,
                description=c.description or "",
                author_name=c.author_name or "",
                created_by=c.created_by,
                is_public=c.is_public,
                created_at=c.created_at,
                workout_count=counts.get(c.id, 0),
            )
            for c in cycles
        ]

    async def get_cycle(self, cycle_id: str, user_id: int) -> CycleDetailOut:
        c = await self.repo.get_by_id(cycle_id)
        if not c:
            raise HTTPException(status_code=404, detail="Цикл не найден")
        if not c.is_public and c.created_by != user_id:
            raise HTTPException(status_code=403, detail="Нет доступа")
        return self._to_detail(c)

    async def create_cycle(self, data: CycleCreate, user_id: int) -> CycleDetailOut:
        c = await self.repo.create(
            created_by=user_id,
            title=data.title,
            description=data.description,
            author_name=data.author_name,
            is_public=data.is_public,
            workouts_data=data.workouts,
        )
        return self._to_detail(c)

    async def update_cycle(self, cycle_id: str, data: CycleUpdate, user_id: int) -> CycleDetailOut:
        c = await self.repo.get_by_id(cycle_id)
        if not c:
            raise HTTPException(status_code=404, detail="Цикл не найден")
        if c.created_by != user_id:
            raise HTTPException(status_code=403, detail="Нет доступа")
        c = await self.repo.update(
            c,
            title=data.title,
            description=data.description,
            author_name=data.author_name,
            is_public=data.is_public,
            workouts_data=data.workouts,
        )
        return self._to_detail(c)

    async def delete_cycle(self, cycle_id: str, user_id: int) -> None:
        c = await self.repo.get_by_id(cycle_id)
        if not c:
            raise HTTPException(status_code=404, detail="Цикл не найден")
        if c.created_by != user_id:
            raise HTTPException(status_code=403, detail="Нет доступа")
        await self.repo.delete(c)

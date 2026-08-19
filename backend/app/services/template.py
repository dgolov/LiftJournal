from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    WorkoutTemplateCreate, WorkoutTemplateUpdate, WorkoutTemplateOut, TemplateExerciseOut,
)
from app.domain.models import WorkoutTemplate
from app.repositories.template import TemplateRepository


class TemplateService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = TemplateRepository(db)

    def _to_dto(self, t: WorkoutTemplate) -> WorkoutTemplateOut:
        return WorkoutTemplateOut(
            id=t.id,
            title=t.title,
            type=t.type,
            createdAt=t.created_at,
            exercises=[
                TemplateExerciseOut(
                    exerciseId=ex.exercise_id,
                    exerciseName=ex.exercise_name,
                    targetSets=ex.target_sets,
                )
                for ex in t.exercises
            ],
        )

    async def get_all(self, user_id: int) -> list[WorkoutTemplateOut]:
        return [self._to_dto(t) for t in await self.repo.get_all_by_user(user_id)]

    async def create(self, data: WorkoutTemplateCreate, user_id: int) -> WorkoutTemplateOut:
        t = await self.repo.create(
            user_id=user_id,
            title=data.title,
            type=data.type,
            exercises_data=data.exercises,
        )
        return self._to_dto(t)

    async def update(self, template_id: str, data: WorkoutTemplateUpdate, user_id: int) -> WorkoutTemplateOut:
        t = await self.repo.get_by_id(template_id)
        if not t:
            raise HTTPException(status_code=404, detail="Template not found")
        if t.user_id != user_id:
            raise HTTPException(status_code=403, detail="Нет доступа")
        t = await self.repo.update(
            t,
            title=data.title,
            type=data.type,
            exercises_data=data.exercises,
        )
        return self._to_dto(t)

    async def delete(self, template_id: str, user_id: int) -> None:
        t = await self.repo.get_by_id(template_id)
        if not t:
            raise HTTPException(status_code=404, detail="Template not found")
        if t.user_id != user_id:
            raise HTTPException(status_code=403, detail="Нет доступа")
        await self.repo.delete(t)

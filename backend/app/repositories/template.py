from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import WorkoutTemplate, TemplateExercise


class TemplateRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _eager(self):
        return selectinload(WorkoutTemplate.exercises)

    async def get_all_by_user(self, user_id: int) -> list[WorkoutTemplate]:
        result = await self.db.execute(
            select(WorkoutTemplate)
            .options(self._eager())
            .where(WorkoutTemplate.user_id == user_id)
            .order_by(WorkoutTemplate.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, template_id: str) -> WorkoutTemplate | None:
        result = await self.db.execute(
            select(WorkoutTemplate).options(self._eager()).where(WorkoutTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    async def create(self, *, user_id: int, title: str, type: str, exercises_data: list) -> WorkoutTemplate:
        template = WorkoutTemplate(
            user_id=user_id,
            title=title,
            type=type,
            created_at=datetime.utcnow(),
        )
        template.exercises = self._build_exercises(exercises_data)
        self.db.add(template)
        await self.db.commit()
        return await self.get_by_id(template.id)  # type: ignore[return-value]

    async def update(self, template: WorkoutTemplate, *, title=None, type=None, exercises_data=None) -> WorkoutTemplate:
        if title is not None:
            template.title = title
        if type is not None:
            template.type = type
        if exercises_data is not None:
            template.exercises = self._build_exercises(exercises_data)
        await self.db.commit()
        return await self.get_by_id(template.id)  # type: ignore[return-value]

    async def delete(self, template: WorkoutTemplate) -> None:
        await self.db.delete(template)
        await self.db.commit()

    def _build_exercises(self, exercises_data: list) -> list[TemplateExercise]:
        return [
            TemplateExercise(
                exercise_id=ex.exerciseId,
                exercise_name=ex.exerciseName,
                target_sets=ex.targetSets,
                order=i,
            )
            for i, ex in enumerate(exercises_data)
        ]

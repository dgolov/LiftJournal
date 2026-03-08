from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import Exercise


class ExerciseRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all(self) -> list[Exercise]:
        result = await self.db.execute(select(Exercise).order_by(Exercise.name))
        return list(result.scalars().all())

    async def create(
        self,
        *,
        name: str,
        muscle_group: str,
        secondary_muscles: list,
        equipment: str,
        description: str,
    ) -> Exercise:
        exercise = Exercise(
            name=name,
            muscle_group=muscle_group,
            secondary_muscles=secondary_muscles,
            equipment=equipment,
            description=description,
            is_custom=True,
        )
        self.db.add(exercise)
        await self.db.commit()
        await self.db.refresh(exercise)
        return exercise

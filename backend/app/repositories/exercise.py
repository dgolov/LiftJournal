from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import Exercise


class ExerciseRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all(self, user_id: int) -> list[Exercise]:
        # An approved exercise is visible to everyone; anything else (pending,
        # private, rejected) is visible only to the user who submitted it.
        result = await self.db.execute(
            select(Exercise)
            .where(or_(
                Exercise.status == "approved",
                Exercise.created_by == user_id,
            ))
            .order_by(Exercise.name)
        )
        return list(result.scalars().all())

    async def create(
        self,
        *,
        name: str,
        muscle_group: str,
        secondary_muscles: list,
        equipment: str,
        description: str,
        created_by: int,
        is_private: bool = False,
    ) -> Exercise:
        exercise = Exercise(
            name=name,
            muscle_group=muscle_group,
            secondary_muscles=secondary_muscles,
            equipment=equipment,
            description=description,
            is_custom=True,
            status="private" if is_private else "pending",
            created_by=created_by,
        )
        self.db.add(exercise)
        await self.db.commit()
        await self.db.refresh(exercise)
        return exercise

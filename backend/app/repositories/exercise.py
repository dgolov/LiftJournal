from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import Exercise


class ExerciseRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all(self, user_id: int) -> list[Exercise]:
        # Approved + public exercises are visible to everyone; a pending or
        # private exercise is visible only to the user who submitted it.
        result = await self.db.execute(
            select(Exercise)
            .where(or_(
                (Exercise.is_approved.is_(True)) & (Exercise.is_private.is_(False)),
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
            is_approved=False,
            is_private=is_private,
            created_by=created_by,
        )
        self.db.add(exercise)
        await self.db.commit()
        await self.db.refresh(exercise)
        return exercise

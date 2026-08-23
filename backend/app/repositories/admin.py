from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import User, Exercise


class AdminRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all_users(self) -> list[User]:
        result = await self.db.execute(select(User).order_by(User.id))
        return list(result.scalars().all())

    async def get_pending_exercises(self):
        """Each row is (Exercise, submitting User | None) — an outer join since
        created_by is nullable (built-in exercises have no submitter)."""
        result = await self.db.execute(
            select(Exercise, User)
            .outerjoin(User, Exercise.created_by == User.id)
            .where(Exercise.is_approved.is_(False))
            .order_by(Exercise.name)
        )
        return result.all()

    async def get_exercise_by_id(self, exercise_id: str) -> Exercise | None:
        result = await self.db.execute(select(Exercise).where(Exercise.id == exercise_id))
        return result.scalar_one_or_none()

    async def approve_exercise(self, exercise: Exercise) -> Exercise:
        exercise.is_approved = True
        await self.db.commit()
        await self.db.refresh(exercise)
        return exercise

    async def delete_exercise(self, exercise: Exercise) -> None:
        await self.db.delete(exercise)
        await self.db.commit()

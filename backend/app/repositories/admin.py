from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import User, Exercise


class AdminRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_all_users(self) -> list[User]:
        result = await self.db.execute(select(User).order_by(User.id))
        return list(result.scalars().all())

    async def get_exercises(self, *, pending_only: bool):
        """Each row is (Exercise, submitting User | None) — an outer join since
        created_by is nullable (built-in exercises have no submitter)."""
        query = select(Exercise, User).outerjoin(User, Exercise.created_by == User.id)
        if pending_only:
            query = query.where(
                (Exercise.is_approved.is_(False)) & (Exercise.is_private.is_(False))
            )
        result = await self.db.execute(query.order_by(Exercise.name))
        return result.all()

    async def get_exercise_by_id(self, exercise_id: str) -> Exercise | None:
        result = await self.db.execute(select(Exercise).where(Exercise.id == exercise_id))
        return result.scalar_one_or_none()

    async def approve_exercise(self, exercise: Exercise) -> Exercise:
        exercise.is_approved = True
        exercise.is_private = False
        await self.db.commit()
        await self.db.refresh(exercise)
        return exercise

    async def revoke_exercise(self, exercise: Exercise) -> Exercise:
        exercise.is_approved = False
        exercise.is_private = True
        await self.db.commit()
        await self.db.refresh(exercise)
        return exercise

    async def rename_exercise(self, exercise: Exercise, name: str) -> Exercise:
        exercise.name = name
        await self.db.commit()
        await self.db.refresh(exercise)
        return exercise

    async def delete_exercise(self, exercise: Exercise) -> None:
        await self.db.delete(exercise)
        await self.db.commit()

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import User, WeightEntry, Goal, UserMax


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_with_relations(self, user_id: int) -> User | None:
        result = await self.db.execute(
            select(User)
            .options(
                selectinload(User.weight_log),
                selectinload(User.goals),
                selectinload(User.maxes),
            )
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, *, email: str, hashed_password: str, name: str) -> User:
        user = User(email=email, hashed_password=hashed_password, name=name, age=0)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_profile(
        self,
        user: User,
        *,
        name: str | None,
        age: int | None,
        avatar_url: str | None,
    ) -> User:
        if name is not None:
            user.name = name
        if age is not None:
            user.age = age
        if avatar_url is not None:
            user.avatar_url = avatar_url
        await self.db.commit()
        return await self.get_with_relations(user.id)  # type: ignore[return-value]

    async def upsert_weight(self, user_id: int, entry_date: date, kg: float) -> WeightEntry:
        result = await self.db.execute(
            select(WeightEntry).where(
                WeightEntry.user_id == user_id, WeightEntry.date == entry_date
            )
        )
        entry = result.scalar_one_or_none()
        if entry:
            entry.kg = kg
        else:
            entry = WeightEntry(user_id=user_id, date=entry_date, kg=kg)
            self.db.add(entry)
        await self.db.commit()
        return entry

    async def delete_weight(self, user_id: int, entry_date: date) -> None:
        result = await self.db.execute(
            select(WeightEntry).where(
                WeightEntry.user_id == user_id, WeightEntry.date == entry_date
            )
        )
        entry = result.scalar_one_or_none()
        if entry:
            await self.db.delete(entry)
            await self.db.commit()

    async def create_goal(
        self, user_id: int, text: str, target_date: date | None, done: bool
    ) -> Goal:
        goal = Goal(user_id=user_id, text=text, target_date=target_date, done=done)
        self.db.add(goal)
        await self.db.commit()
        await self.db.refresh(goal)
        return goal

    async def toggle_goal(self, user_id: int, goal_id: str) -> Goal | None:
        result = await self.db.execute(
            select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id)
        )
        goal = result.scalar_one_or_none()
        if goal:
            goal.done = not goal.done
            await self.db.commit()
        return goal

    async def delete_goal(self, user_id: int, goal_id: str) -> None:
        result = await self.db.execute(
            select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id)
        )
        goal = result.scalar_one_or_none()
        if goal:
            await self.db.delete(goal)
            await self.db.commit()

    async def upsert_max(
        self, user_id: int, exercise_name: str, weight_kg: float
    ) -> UserMax:
        result = await self.db.execute(
            select(UserMax).where(
                UserMax.user_id == user_id, UserMax.exercise_name == exercise_name
            )
        )
        entry = result.scalar_one_or_none()
        if entry:
            entry.weight_kg = weight_kg
            entry.recorded_at = date.today()
        else:
            entry = UserMax(user_id=user_id, exercise_name=exercise_name, weight_kg=weight_kg)
            self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def delete_max(self, user_id: int, exercise_name: str) -> None:
        result = await self.db.execute(
            select(UserMax).where(
                UserMax.user_id == user_id, UserMax.exercise_name == exercise_name
            )
        )
        entry = result.scalar_one_or_none()
        if entry:
            await self.db.delete(entry)
            await self.db.commit()

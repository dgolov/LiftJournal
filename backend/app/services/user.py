from datetime import date

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    UserOut, WeightEntryOut, GoalOut, UserMaxOut,
    ProfileUpdate, WeightEntryIn, GoalCreate, UserMaxIn, ThemeUpdate,
)
from app.repositories.user import UserRepository
from app.domain.models import User


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)

    def _to_dto(self, u: User) -> UserOut:
        return UserOut(
            name=u.name,
            birthDate=u.birth_date,
            avatarUrl=u.avatar_url,
            theme=u.theme if u.theme else "light",
            weightLog=sorted(
                [WeightEntryOut(date=e.date, kg=e.kg) for e in u.weight_log],
                key=lambda x: x.date,
            ),
            goals=[
                GoalOut(id=g.id, text=g.text, targetDate=g.target_date, done=g.done)
                for g in u.goals
            ],
            maxes=[
                UserMaxOut(exercise_name=m.exercise_name, weight_kg=m.weight_kg, recorded_at=m.recorded_at)
                for m in u.maxes
            ],
        )

    async def get_user(self, user_id: int) -> UserOut:
        u = await self.repo.get_with_relations(user_id)
        if not u:
            raise HTTPException(status_code=404, detail="User not found")
        return self._to_dto(u)

    async def update_profile(self, user_id: int, data: ProfileUpdate) -> UserOut:
        u = await self.repo.get_with_relations(user_id)
        if not u:
            raise HTTPException(status_code=404, detail="User not found")
        u = await self.repo.update_profile(u, name=data.name, birth_date=data.birthDate, avatar_url=data.avatarUrl)
        return self._to_dto(u)

    async def log_weight(self, user_id: int, data: WeightEntryIn) -> WeightEntryOut:
        entry = await self.repo.upsert_weight(user_id, data.date, data.kg)
        return WeightEntryOut(date=entry.date, kg=entry.kg)

    async def delete_weight(self, user_id: int, entry_date_str: str) -> None:
        try:
            d = date.fromisoformat(entry_date_str)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid date format")
        await self.repo.delete_weight(user_id, d)

    async def create_goal(self, user_id: int, data: GoalCreate) -> GoalOut:
        goal = await self.repo.create_goal(user_id, data.text, data.targetDate, data.done)
        return GoalOut(id=goal.id, text=goal.text, targetDate=goal.target_date, done=goal.done)

    async def toggle_goal(self, user_id: int, goal_id: str) -> GoalOut:
        goal = await self.repo.toggle_goal(user_id, goal_id)
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        return GoalOut(id=goal.id, text=goal.text, targetDate=goal.target_date, done=goal.done)

    async def delete_goal(self, user_id: int, goal_id: str) -> None:
        await self.repo.delete_goal(user_id, goal_id)

    async def upsert_max(self, user_id: int, data: UserMaxIn) -> UserMaxOut:
        entry = await self.repo.upsert_max(user_id, data.exercise_name, data.weight_kg)
        return UserMaxOut(
            exercise_name=entry.exercise_name,
            weight_kg=entry.weight_kg,
            recorded_at=entry.recorded_at,
        )

    async def delete_max(self, user_id: int, exercise_name: str) -> None:
        await self.repo.delete_max(user_id, exercise_name)

    async def update_theme(self, user_id: int, data: ThemeUpdate) -> UserOut:
        u = await self.repo.update_theme(user_id, data.theme)
        if not u:
            raise HTTPException(status_code=404, detail="User not found")
        return self._to_dto(u)

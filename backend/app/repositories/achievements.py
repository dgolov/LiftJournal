from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import UserAchievement


class AchievementRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_for_user(self, user_id: int) -> list[UserAchievement]:
        result = await self.db.execute(
            select(UserAchievement).where(UserAchievement.user_id == user_id)
        )
        return list(result.scalars().all())

    async def unlock(self, *, user_id: int, achievement_id: str, unlocked_at: datetime) -> UserAchievement:
        row = UserAchievement(user_id=user_id, achievement_id=achievement_id, unlocked_at=unlocked_at)
        self.db.add(row)
        await self.db.commit()
        return row

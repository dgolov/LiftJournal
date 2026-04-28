from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import Notification, User, Workout





class NotificationRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self, user_id: int, type: str, actor_id: int,
        workout_id: str | None = None, comment_text: str | None = None,
    ) -> Notification:
        # Deduplicate: remove existing unread notification of same type/actor/workout
        existing = await self.db.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.type == type,
                Notification.actor_id == actor_id,
                Notification.workout_id == workout_id,
                Notification.is_read == False,
            )
        )
        old = existing.scalar_one_or_none()
        if old:
            await self.db.delete(old)

        n = Notification(user_id=user_id, type=type, actor_id=actor_id,
                         workout_id=workout_id, comment_text=comment_text)
        self.db.add(n)
        await self.db.commit()
        await self.db.refresh(n)
        return n

    async def get_unread_count(self, user_id: int) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
        )
        return result.scalar() or 0

    async def get_page(
        self, user_id: int, unread_only: bool, page: int, per_page: int
    ) -> tuple[list, int]:
        q = select(Notification, User, Workout).where(Notification.user_id == user_id)
        if unread_only:
            q = q.where(Notification.is_read == False)
        q = (q
             .join(User, User.id == Notification.actor_id)
             .outerjoin(Workout, Workout.id == Notification.workout_id)
             .order_by(desc(Notification.created_at)))

        total_result = await self.db.execute(
            select(func.count()).select_from(Notification)
            .where(Notification.user_id == user_id,
                   *([] if not unread_only else [Notification.is_read == False]))
        )
        total = total_result.scalar() or 0

        rows = await self.db.execute(q.offset((page - 1) * per_page).limit(per_page))
        return rows.all(), total

    async def mark_read(self, notification_id: str, user_id: int) -> None:
        result = await self.db.execute(
            select(Notification).where(
                Notification.id == notification_id, Notification.user_id == user_id
            )
        )
        n = result.scalar_one_or_none()
        if n and not n.is_read:
            n.is_read = True
            await self.db.commit()

    async def get_actor(self, actor_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == actor_id))
        return result.scalar_one_or_none()

    async def get_workout_title(self, workout_id: str) -> str | None:
        result = await self.db.execute(select(Workout.title).where(Workout.id == workout_id))
        return result.scalar_one_or_none()

    async def mark_all_read(self, user_id: int) -> None:
        result = await self.db.execute(
            select(Notification).where(
                Notification.user_id == user_id, Notification.is_read == False
            )
        )
        for n in result.scalars().all():
            n.is_read = True
        await self.db.commit()

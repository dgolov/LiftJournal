from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import NotificationOut, NotificationsPageOut, UnreadCountOut
from app.repositories.notifications import NotificationRepository
from app.core.ws_manager import manager


class NotificationService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = NotificationRepository(db)

    # ── Internal triggers ─────────────────────────────────────────────────────

    async def _create_and_push(
        self, user_id: int, type: str, actor_id: int,
        workout_id: str | None = None, comment_text: str | None = None,
    ) -> None:
        n = await self.repo.create(
            user_id=user_id, type=type, actor_id=actor_id,
            workout_id=workout_id, comment_text=comment_text,
        )
        actor = await self.repo.get_actor(actor_id)
        workout_title = await self.repo.get_workout_title(workout_id) if workout_id else None
        await manager.send(user_id, {
            "event": "notification",
            "data": {
                "id": n.id,
                "type": n.type,
                "actorId": actor_id,
                "actorName": actor.name if actor else "",
                "workoutId": workout_id,
                "workoutTitle": workout_title,
                "commentText": n.comment_text,
                "isRead": False,
                "createdAt": n.created_at.isoformat(),
            },
        })

    async def notify_follow(self, actor_id: int, target_user_id: int) -> None:
        if actor_id == target_user_id:
            return
        await self._create_and_push(user_id=target_user_id, type="follow", actor_id=actor_id)

    async def notify_like(self, actor_id: int, workout_owner_id: int, workout_id: str) -> None:
        if actor_id == workout_owner_id:
            return
        await self._create_and_push(user_id=workout_owner_id, type="like",
                                    actor_id=actor_id, workout_id=workout_id)

    async def notify_comment(
        self, actor_id: int, workout_owner_id: int, workout_id: str, comment_text: str
    ) -> None:
        if actor_id == workout_owner_id:
            return
        await self._create_and_push(
            user_id=workout_owner_id, type="comment",
            actor_id=actor_id, workout_id=workout_id,
            comment_text=comment_text[:100] if comment_text else None,
        )

    # ── Public API ────────────────────────────────────────────────────────────

    async def get_unread_count(self, user_id: int) -> UnreadCountOut:
        return UnreadCountOut(count=await self.repo.get_unread_count(user_id))

    async def get_notifications(
        self, user_id: int, unread_only: bool, page: int, per_page: int
    ) -> NotificationsPageOut:
        rows, total = await self.repo.get_page(user_id, unread_only, page, per_page)
        items = [
            NotificationOut(
                id=n.id,
                type=n.type,
                actorId=u.id,
                actorName=u.name,
                workoutId=n.workout_id,
                workoutTitle=w.title if w else None,
                commentText=n.comment_text,
                isRead=n.is_read,
                createdAt=n.created_at,
            )
            for n, u, w in rows
        ]
        has_more = (page * per_page) < total
        return NotificationsPageOut(items=items, hasMore=has_more, total=total)

    async def mark_read(self, notification_id: str, user_id: int) -> None:
        await self.repo.mark_read(notification_id, user_id)

    async def mark_all_read(self, user_id: int) -> None:
        await self.repo.mark_all_read(user_id)

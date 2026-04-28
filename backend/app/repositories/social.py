from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import date, timedelta

from app.domain.models import User, UserFollow, Workout, WorkoutExercise, WorkoutLike, WorkoutComment, UserMax, Goal, UserAchievement


class SocialRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def search_users(self, query: str, current_user_id: int) -> list[User]:
        result = await self.db.execute(
            select(User)
            .where(User.name.ilike(f"%{query}%"), User.id != current_user_id)
            .order_by(User.name)
            .limit(20)
        )
        return list(result.scalars().all())

    async def get_user_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def followers_count(self, user_id: int) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(UserFollow).where(UserFollow.following_id == user_id)
        )
        return result.scalar() or 0

    async def following_count(self, user_id: int) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(UserFollow).where(UserFollow.follower_id == user_id)
        )
        return result.scalar() or 0

    async def workouts_count(self, user_id: int) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Workout).where(Workout.user_id == user_id)
        )
        return result.scalar() or 0

    async def is_following(self, follower_id: int, following_id: int) -> bool:
        result = await self.db.execute(
            select(UserFollow).where(
                UserFollow.follower_id == follower_id,
                UserFollow.following_id == following_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def follow(self, follower_id: int, following_id: int) -> None:
        if not await self.is_following(follower_id, following_id):
            self.db.add(UserFollow(follower_id=follower_id, following_id=following_id))
            await self.db.commit()

    async def unfollow(self, follower_id: int, following_id: int) -> None:
        result = await self.db.execute(
            select(UserFollow).where(
                UserFollow.follower_id == follower_id,
                UserFollow.following_id == following_id,
            )
        )
        follow = result.scalar_one_or_none()
        if follow:
            await self.db.delete(follow)
            await self.db.commit()

    async def get_followers(self, user_id: int) -> list[User]:
        result = await self.db.execute(
            select(User)
            .join(UserFollow, UserFollow.follower_id == User.id)
            .where(UserFollow.following_id == user_id)
            .order_by(User.name)
        )
        return list(result.scalars().all())

    async def get_following(self, user_id: int) -> list[User]:
        result = await self.db.execute(
            select(User)
            .join(UserFollow, UserFollow.following_id == User.id)
            .where(UserFollow.follower_id == user_id)
            .order_by(User.name)
        )
        return list(result.scalars().all())

    async def get_user_workouts(self, user_id: int) -> list[Workout]:
        result = await self.db.execute(
            select(Workout)
            .options(selectinload(Workout.exercises).selectinload(WorkoutExercise.sets))
            .where(Workout.user_id == user_id)
            .order_by(Workout.date.desc(), Workout.created_at.desc())
            .limit(50)
        )
        return list(result.scalars().all())

    # ── Public profile extras ─────────────────────────────────────────────────

    async def get_user_activity(self, user_id: int) -> list:
        year_ago = date.today() - timedelta(days=365)
        result = await self.db.execute(
            select(Workout.date, func.count().label("cnt"))
            .where(Workout.user_id == user_id, Workout.date >= year_ago)
            .group_by(Workout.date)
            .order_by(Workout.date)
        )
        return result.all()

    async def get_user_maxes(self, user_id: int) -> list[UserMax]:
        result = await self.db.execute(
            select(UserMax).where(UserMax.user_id == user_id).order_by(UserMax.exercise_name)
        )
        return list(result.scalars().all())

    async def get_user_goals(self, user_id: int) -> list[Goal]:
        result = await self.db.execute(
            select(Goal)
            .where(Goal.user_id == user_id, Goal.done == False)
            .order_by(Goal.target_date)
        )
        return list(result.scalars().all())

    async def get_user_achievements_raw(self, user_id: int) -> list[UserAchievement]:
        result = await self.db.execute(
            select(UserAchievement)
            .where(UserAchievement.user_id == user_id)
            .order_by(UserAchievement.unlocked_at.desc())
        )
        return list(result.scalars().all())

    # ── Likes ────────────────────────────────────────────────────────────────

    async def toggle_like(self, user_id: int, workout_id: str) -> bool:
        result = await self.db.execute(
            select(WorkoutLike).where(WorkoutLike.user_id == user_id, WorkoutLike.workout_id == workout_id)
        )
        like = result.scalar_one_or_none()
        if like:
            await self.db.delete(like)
            await self.db.commit()
            return False
        self.db.add(WorkoutLike(user_id=user_id, workout_id=workout_id))
        await self.db.commit()
        return True

    async def get_likes_count(self, workout_id: str) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(WorkoutLike).where(WorkoutLike.workout_id == workout_id)
        )
        return result.scalar() or 0

    async def is_liked(self, user_id: int, workout_id: str) -> bool:
        result = await self.db.execute(
            select(WorkoutLike).where(WorkoutLike.user_id == user_id, WorkoutLike.workout_id == workout_id)
        )
        return result.scalar_one_or_none() is not None

    async def get_likes_batch(self, workout_ids: list[str], user_id: int) -> dict[str, tuple[int, bool]]:
        if not workout_ids:
            return {}
        counts_result = await self.db.execute(
            select(WorkoutLike.workout_id, func.count().label("cnt"))
            .where(WorkoutLike.workout_id.in_(workout_ids))
            .group_by(WorkoutLike.workout_id)
        )
        counts_map = {row.workout_id: row.cnt for row in counts_result}
        liked_result = await self.db.execute(
            select(WorkoutLike.workout_id)
            .where(WorkoutLike.workout_id.in_(workout_ids), WorkoutLike.user_id == user_id)
        )
        liked_set = {row.workout_id for row in liked_result}
        return {wid: (counts_map.get(wid, 0), wid in liked_set) for wid in workout_ids}

    # ── Comments ─────────────────────────────────────────────────────────────

    async def get_comments(self, workout_id: str) -> list:
        result = await self.db.execute(
            select(WorkoutComment, User)
            .join(User, User.id == WorkoutComment.user_id)
            .where(WorkoutComment.workout_id == workout_id)
            .order_by(WorkoutComment.created_at.asc())
        )
        return result.all()

    async def add_comment(self, user_id: int, workout_id: str, text: str) -> WorkoutComment:
        comment = WorkoutComment(user_id=user_id, workout_id=workout_id, text=text)
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def delete_comment(self, comment_id: str, user_id: int) -> bool:
        result = await self.db.execute(
            select(WorkoutComment).where(WorkoutComment.id == comment_id, WorkoutComment.user_id == user_id)
        )
        comment = result.scalar_one_or_none()
        if not comment:
            return False
        await self.db.delete(comment)
        await self.db.commit()
        return True

    async def get_comments_count_batch(self, workout_ids: list[str]) -> dict[str, int]:
        if not workout_ids:
            return {}
        result = await self.db.execute(
            select(WorkoutComment.workout_id, func.count().label("cnt"))
            .where(WorkoutComment.workout_id.in_(workout_ids))
            .group_by(WorkoutComment.workout_id)
        )
        return {row.workout_id: row.cnt for row in result}

    async def get_feed(self, user_id: int, limit: int = 30, offset: int = 0) -> list[Workout]:
        following_subq = select(UserFollow.following_id).where(UserFollow.follower_id == user_id)
        result = await self.db.execute(
            select(Workout)
            .options(selectinload(Workout.exercises).selectinload(WorkoutExercise.sets))
            .where(Workout.user_id.in_(following_subq))
            .order_by(Workout.date.desc(), Workout.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

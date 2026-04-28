from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import date

from app.api.schemas import (
    UserPublicOut, UserSearchOut, FollowStatusOut,
    FeedWorkoutOut, WorkoutExerciseOut, SetOut,
    LikeStatusOut, WorkoutCommentIn, WorkoutCommentOut,
    ActivityDayOut, PublicMaxOut, PublicGoalOut, PublicAchievementOut,
    WorkoutMetaOut,
)
from app.repositories.social import SocialRepository


class SocialService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = SocialRepository(db)

    async def search_users(self, query: str, current_user_id: int) -> list[UserSearchOut]:
        if len(query.strip()) < 2:
            return []
        users = await self.repo.search_users(query.strip(), current_user_id)
        result = []
        for u in users:
            result.append(UserSearchOut(
                id=u.id,
                name=u.name,
                avatarUrl=u.avatar_url,
                isFollowing=await self.repo.is_following(current_user_id, u.id),
            ))
        return result

    async def get_public_profile(self, user_id: int, current_user_id: int) -> UserPublicOut:
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        age = None
        if user.birth_date:
            today = date.today()
            age = today.year - user.birth_date.year - (
                (today.month, today.day) < (user.birth_date.month, user.birth_date.day)
            )
        return UserPublicOut(
            id=user.id,
            name=user.name,
            avatarUrl=user.avatar_url,
            age=age,
            followersCount=await self.repo.followers_count(user_id),
            followingCount=await self.repo.following_count(user_id),
            workoutsCount=await self.repo.workouts_count(user_id),
            isFollowing=await self.repo.is_following(current_user_id, user_id),
        )

    async def get_user_activity(self, user_id: int) -> list[ActivityDayOut]:
        await self._require_user(user_id)
        rows = await self.repo.get_user_activity(user_id)
        return [ActivityDayOut(date=str(r.date), count=r.cnt) for r in rows]

    async def get_user_public_maxes(self, user_id: int) -> list[PublicMaxOut]:
        await self._require_user(user_id)
        maxes = await self.repo.get_user_maxes(user_id)
        return [PublicMaxOut(exerciseName=m.exercise_name, weightKg=m.weight_kg) for m in maxes]

    async def get_user_public_goals(self, user_id: int) -> list[PublicGoalOut]:
        await self._require_user(user_id)
        goals = await self.repo.get_user_goals(user_id)
        return [PublicGoalOut(text=g.text, targetDate=g.target_date) for g in goals]

    async def get_user_public_achievements(self, user_id: int) -> list[PublicAchievementOut]:
        await self._require_user(user_id)
        from app.services.achievements import REGISTRY_MAP
        raw = await self.repo.get_user_achievements_raw(user_id)
        result = []
        for ua in raw:
            defn = REGISTRY_MAP.get(ua.achievement_id)
            if defn:
                result.append(PublicAchievementOut(
                    id=ua.achievement_id, title=defn.title, icon=defn.icon,
                    category=defn.category, unlockedAt=ua.unlocked_at,
                ))
        return result

    async def _require_user(self, user_id: int) -> None:
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

    async def follow(self, follower_id: int, following_id: int) -> FollowStatusOut:
        if follower_id == following_id:
            raise HTTPException(status_code=400, detail="Нельзя подписаться на себя")
        user = await self.repo.get_user_by_id(following_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        await self.repo.follow(follower_id, following_id)
        from app.services.notifications import NotificationService
        await NotificationService(self.repo.db).notify_follow(follower_id, following_id)
        return FollowStatusOut(
            isFollowing=True,
            followersCount=await self.repo.followers_count(following_id),
        )

    async def unfollow(self, follower_id: int, following_id: int) -> FollowStatusOut:
        await self.repo.unfollow(follower_id, following_id)
        return FollowStatusOut(
            isFollowing=False,
            followersCount=await self.repo.followers_count(following_id),
        )

    def _workout_to_dto(self, w, user, likes_count=0, comments_count=0, is_liked=False) -> FeedWorkoutOut:
        return FeedWorkoutOut(
            id=w.id,
            date=w.date,
            type=w.type,
            title=w.title,
            durationMinutes=w.duration_minutes,
            notes=w.notes or "",
            createdAt=w.created_at,
            exercises=[
                WorkoutExerciseOut(
                    exerciseId=ex.exercise_id,
                    exerciseName=ex.exercise_name,
                    sets=[
                        SetOut(id=s.id, weight=s.weight, reps=s.reps, completed=s.completed, failed=s.failed)
                        for s in ex.sets
                    ],
                )
                for ex in w.exercises
            ],
            userId=user.id,
            userName=user.name,
            userAvatarUrl=user.avatar_url,
            likesCount=likes_count,
            commentsCount=comments_count,
            isLiked=is_liked,
        )

    async def _get_workout_model(self, workout_id: str):
        from sqlalchemy import select
        from app.domain.models import Workout
        result = await self.repo.db.execute(select(Workout).where(Workout.id == workout_id))
        w = result.scalar_one_or_none()
        if not w:
            raise HTTPException(status_code=404, detail="Тренировка не найдена")
        return w

    async def get_followers(self, user_id: int) -> list[UserSearchOut]:
        users = await self.repo.get_followers(user_id)
        return [UserSearchOut(
            id=u.id, name=u.name, avatarUrl=u.avatar_url,
            isFollowing=await self.repo.is_following(user_id, u.id),
        ) for u in users]

    async def get_following(self, user_id: int) -> list[UserSearchOut]:
        users = await self.repo.get_following(user_id)
        return [UserSearchOut(
            id=u.id, name=u.name, avatarUrl=u.avatar_url,
            isFollowing=True,
        ) for u in users]

    async def get_workout(self, workout_id: str, current_user_id: int) -> FeedWorkoutOut:
        from app.domain.models import Workout, WorkoutExercise
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        result = await self.repo.db.execute(
            select(Workout)
            .options(selectinload(Workout.exercises).selectinload(WorkoutExercise.sets))
            .where(Workout.id == workout_id)
        )
        w = result.scalar_one_or_none()
        if not w:
            raise HTTPException(status_code=404, detail="Тренировка не найдена")
        user = await self.repo.get_user_by_id(w.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Тренировка не найдена")
        likes_data = await self.repo.get_likes_batch([w.id], current_user_id)
        comments_data = await self.repo.get_comments_count_batch([w.id])
        lc, il = likes_data.get(w.id, (0, False))
        return self._workout_to_dto(w, user, likes_count=lc, comments_count=comments_data.get(w.id, 0), is_liked=il)

    async def get_user_workouts(self, target_user_id: int, current_user_id: int) -> list[FeedWorkoutOut]:
        user = await self.repo.get_user_by_id(target_user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        workouts = await self.repo.get_user_workouts(target_user_id)
        if not workouts:
            return []
        workout_ids = [w.id for w in workouts]
        likes_data = await self.repo.get_likes_batch(workout_ids, current_user_id)
        comments_data = await self.repo.get_comments_count_batch(workout_ids)
        return [
            self._workout_to_dto(
                w, user,
                likes_count=likes_data.get(w.id, (0, False))[0],
                comments_count=comments_data.get(w.id, 0),
                is_liked=likes_data.get(w.id, (0, False))[1],
            )
            for w in workouts
        ]

    async def get_feed(self, user_id: int, limit: int = 30, offset: int = 0) -> list[FeedWorkoutOut]:
        workouts = await self.repo.get_feed(user_id, limit, offset)
        if not workouts:
            return []
        workout_ids = [w.id for w in workouts]
        user_ids = list({w.user_id for w in workouts})
        users = {}
        for uid in user_ids:
            u = await self.repo.get_user_by_id(uid)
            if u:
                users[uid] = u
        likes_data = await self.repo.get_likes_batch(workout_ids, user_id)
        comments_data = await self.repo.get_comments_count_batch(workout_ids)
        return [
            self._workout_to_dto(
                w, users[w.user_id],
                likes_count=likes_data.get(w.id, (0, False))[0],
                comments_count=comments_data.get(w.id, 0),
                is_liked=likes_data.get(w.id, (0, False))[1],
            )
            for w in workouts if w.user_id in users
        ]

    async def toggle_like(self, current_user_id: int, workout_id: str) -> LikeStatusOut:
        w = await self._get_workout_model(workout_id)
        if w.user_id != current_user_id and not await self.repo.is_following(current_user_id, w.user_id):
            raise HTTPException(status_code=403, detail="Нет доступа")
        is_liked = await self.repo.toggle_like(current_user_id, workout_id)
        likes_count = await self.repo.get_likes_count(workout_id)
        if is_liked:
            from app.services.notifications import NotificationService
            await NotificationService(self.repo.db).notify_like(current_user_id, w.user_id, workout_id)
        return LikeStatusOut(isLiked=is_liked, likesCount=likes_count)

    async def get_comments(self, workout_id: str, current_user_id: int) -> list[WorkoutCommentOut]:
        w = await self._get_workout_model(workout_id)
        if w.user_id != current_user_id and not await self.repo.is_following(current_user_id, w.user_id):
            raise HTTPException(status_code=403, detail="Нет доступа")
        rows = await self.repo.get_comments(workout_id)
        return [
            WorkoutCommentOut(
                id=c.id, userId=u.id, userName=u.name,
                text=c.text, createdAt=c.created_at,
                isOwn=(u.id == current_user_id),
            )
            for c, u in rows
        ]

    async def add_comment(self, current_user_id: int, workout_id: str, text: str) -> WorkoutCommentOut:
        text = text.strip()
        if not text:
            raise HTTPException(status_code=422, detail="Комментарий не может быть пустым")
        w = await self._get_workout_model(workout_id)
        if w.user_id != current_user_id and not await self.repo.is_following(current_user_id, w.user_id):
            raise HTTPException(status_code=403, detail="Нет доступа")
        user = await self.repo.get_user_by_id(current_user_id)
        comment = await self.repo.add_comment(current_user_id, workout_id, text)
        from app.services.notifications import NotificationService
        await NotificationService(self.repo.db).notify_comment(current_user_id, w.user_id, workout_id, text)
        return WorkoutCommentOut(
            id=comment.id, userId=user.id, userName=user.name,
            text=comment.text, createdAt=comment.created_at, isOwn=True,
        )

    async def get_workouts_meta(self, workout_ids: list[str], current_user_id: int) -> list[WorkoutMetaOut]:
        if not workout_ids:
            return []
        likes_data = await self.repo.get_likes_batch(workout_ids, current_user_id)
        comments_data = await self.repo.get_comments_count_batch(workout_ids)
        return [
            WorkoutMetaOut(
                workoutId=wid,
                likesCount=likes_data.get(wid, (0, False))[0],
                commentsCount=comments_data.get(wid, 0),
                isLiked=likes_data.get(wid, (0, False))[1],
            )
            for wid in workout_ids
        ]

    async def delete_comment(self, current_user_id: int, comment_id: str) -> None:
        deleted = await self.repo.delete_comment(comment_id, current_user_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Комментарий не найден")

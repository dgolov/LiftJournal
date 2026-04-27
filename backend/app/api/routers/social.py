from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    UserPublicOut, UserSearchOut, FollowStatusOut, FeedWorkoutOut,
    LikeStatusOut, WorkoutCommentIn, WorkoutCommentOut,
    ActivityDayOut, PublicMaxOut, PublicGoalOut, PublicAchievementOut,
    WorkoutMetaOut,
)
from app.core.database import get_db
from app.core.security import get_current_user
from app.domain.models import User
from app.services.social import SocialService

router = APIRouter()


@router.get("/users/search", response_model=list[UserSearchOut])
async def search_users(
    q: str = Query(..., min_length=2),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SocialService(db).search_users(q, current_user.id)


@router.get("/users/{user_id}", response_model=UserPublicOut)
async def get_public_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SocialService(db).get_public_profile(user_id, current_user.id)


@router.post("/users/{user_id}/follow", response_model=FollowStatusOut)
async def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SocialService(db).follow(current_user.id, user_id)


@router.delete("/users/{user_id}/follow", response_model=FollowStatusOut)
async def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SocialService(db).unfollow(current_user.id, user_id)


@router.get("/users/{user_id}/activity", response_model=list[ActivityDayOut])
async def get_user_activity(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SocialService(db).get_user_activity(user_id)


@router.get("/users/{user_id}/maxes", response_model=list[PublicMaxOut])
async def get_user_maxes(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SocialService(db).get_user_public_maxes(user_id)


@router.get("/users/{user_id}/goals", response_model=list[PublicGoalOut])
async def get_user_goals(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SocialService(db).get_user_public_goals(user_id)


@router.get("/users/{user_id}/achievements", response_model=list[PublicAchievementOut])
async def get_user_achievements(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SocialService(db).get_user_public_achievements(user_id)


@router.get("/me/followers", response_model=list[UserSearchOut])
async def get_my_followers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SocialService(db).get_followers(current_user.id)


@router.get("/me/following", response_model=list[UserSearchOut])
async def get_my_following(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SocialService(db).get_following(current_user.id)


@router.get("/workouts/meta", response_model=list[WorkoutMetaOut])
async def get_workouts_meta(
    ids: list[str] = Query(default=[]),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SocialService(db).get_workouts_meta(ids, current_user.id)


@router.get("/workouts/{workout_id}", response_model=FeedWorkoutOut)
async def get_workout(
    workout_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SocialService(db).get_workout(workout_id, current_user.id)


@router.get("/users/{user_id}/workouts", response_model=list[FeedWorkoutOut])
async def get_user_workouts(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SocialService(db).get_user_workouts(user_id, current_user.id)


@router.get("/feed", response_model=list[FeedWorkoutOut])
async def get_feed(
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SocialService(db).get_feed(current_user.id, limit, offset)


@router.post("/workouts/{workout_id}/like", response_model=LikeStatusOut)
async def toggle_like(
    workout_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SocialService(db).toggle_like(current_user.id, workout_id)


@router.get("/workouts/{workout_id}/comments", response_model=list[WorkoutCommentOut])
async def get_comments(
    workout_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SocialService(db).get_comments(workout_id, current_user.id)


@router.post("/workouts/{workout_id}/comments", response_model=WorkoutCommentOut)
async def add_comment(
    workout_id: str,
    body: WorkoutCommentIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SocialService(db).add_comment(current_user.id, workout_id, body.text)


@router.delete("/workouts/{workout_id}/comments/{comment_id}", status_code=204)
async def delete_comment(
    workout_id: str,
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await SocialService(db).delete_comment(current_user.id, comment_id)

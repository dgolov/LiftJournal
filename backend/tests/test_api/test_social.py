from datetime import date, datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.api.schemas import (
    UserPublicOut, UserSearchOut, FollowStatusOut, FeedWorkoutOut,
    LikeStatusOut, WorkoutCommentOut, ActivityDayOut, WorkoutMetaOut,
)


def _user_public(id=2):
    return UserPublicOut(
        id=id, name="Alice", avatarUrl=None, age=25,
        followersCount=10, followingCount=5, workoutsCount=20,
        isFollowing=False,
    )


def _user_search(id=2):
    return UserSearchOut(id=id, name="Alice", avatarUrl=None, isFollowing=False)


def _feed_workout(id="w-1"):
    return FeedWorkoutOut(
        id=id, date=date(2026, 1, 1), type="Силовая", title="Bench Day",
        durationMinutes=60, notes="", createdAt=datetime(2026, 1, 1),
        exercises=[], userId=2, userName="Alice", userAvatarUrl=None,
    )


def _comment(id="c-1"):
    return WorkoutCommentOut(
        id=id, userId=1, userName="Test User",
        text="Great workout!", createdAt=datetime(2026, 1, 1), isOwn=True,
    )


# ── Search ────────────────────────────────────────────────────────────────────

async def test_search_users(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.search_users.return_value = [_user_search()]

        resp = await client.get("/api/social/users/search?q=alice")

    assert resp.status_code == 200
    assert len(resp.json()) == 1
    svc.search_users.assert_called_once_with("alice", 1)


async def test_search_users_too_short_returns_422(client):
    resp = await client.get("/api/social/users/search?q=a")
    assert resp.status_code == 422


# ── Public profile ────────────────────────────────────────────────────────────

async def test_get_public_profile(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_public_profile.return_value = _user_public()

        resp = await client.get("/api/social/users/2")

    assert resp.status_code == 200
    assert resp.json()["id"] == 2
    svc.get_public_profile.assert_called_once_with(2, 1)


async def test_get_public_profile_not_found(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_public_profile.side_effect = HTTPException(404, "Пользователь не найден")

        resp = await client.get("/api/social/users/999")

    assert resp.status_code == 404


# ── Follow / Unfollow ─────────────────────────────────────────────────────────

async def test_follow_user(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.follow.return_value = FollowStatusOut(isFollowing=True, followersCount=11)

        resp = await client.post("/api/social/users/2/follow")

    assert resp.status_code == 200
    assert resp.json()["isFollowing"] is True
    svc.follow.assert_called_once_with(1, 2)


async def test_unfollow_user(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.unfollow.return_value = FollowStatusOut(isFollowing=False, followersCount=10)

        resp = await client.delete("/api/social/users/2/follow")

    assert resp.status_code == 200
    assert resp.json()["isFollowing"] is False
    svc.unfollow.assert_called_once_with(1, 2)


# ── Activity / Maxes / Goals / Achievements ───────────────────────────────────

async def test_get_user_activity(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_user_activity.return_value = [ActivityDayOut(date="2026-01-01", count=2)]

        resp = await client.get("/api/social/users/2/activity")

    assert resp.status_code == 200
    assert resp.json()[0]["count"] == 2


async def test_get_user_maxes(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_user_public_maxes.return_value = []

        resp = await client.get("/api/social/users/2/maxes")

    assert resp.status_code == 200


async def test_get_user_goals(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_user_public_goals.return_value = []

        resp = await client.get("/api/social/users/2/goals")

    assert resp.status_code == 200


async def test_get_user_achievements(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_user_public_achievements.return_value = []

        resp = await client.get("/api/social/users/2/achievements")

    assert resp.status_code == 200


# ── Followers / Following ─────────────────────────────────────────────────────

async def test_get_my_followers(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_followers.return_value = [_user_search()]

        resp = await client.get("/api/social/me/followers")

    assert resp.status_code == 200
    assert len(resp.json()) == 1
    svc.get_followers.assert_called_once_with(1)


async def test_get_my_following(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_following.return_value = []

        resp = await client.get("/api/social/me/following")

    assert resp.status_code == 200
    svc.get_following.assert_called_once_with(1)


# ── Feed ──────────────────────────────────────────────────────────────────────

async def test_get_feed(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_feed.return_value = [_feed_workout()]

        resp = await client.get("/api/social/feed")

    assert resp.status_code == 200
    assert len(resp.json()) == 1
    svc.get_feed.assert_called_once_with(1, 30, 0)


async def test_get_feed_pagination(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_feed.return_value = []

        resp = await client.get("/api/social/feed?limit=10&offset=20")

    svc.get_feed.assert_called_once_with(1, 10, 20)


# ── Workout detail / user workouts ───────────────────────────────────────────

async def test_get_workout(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_workout.return_value = _feed_workout()

        resp = await client.get("/api/social/workouts/w-1")

    assert resp.status_code == 200
    svc.get_workout.assert_called_once_with("w-1", 1)


async def test_get_workout_not_found(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_workout.side_effect = HTTPException(404, "Тренировка не найдена")

        resp = await client.get("/api/social/workouts/missing")

    assert resp.status_code == 404


async def test_get_user_workouts(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_user_workouts.return_value = [_feed_workout()]

        resp = await client.get("/api/social/users/2/workouts")

    assert resp.status_code == 200
    svc.get_user_workouts.assert_called_once_with(2, 1)


# ── Workouts meta ─────────────────────────────────────────────────────────────

async def test_get_workouts_meta(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_workouts_meta.return_value = [
            WorkoutMetaOut(workoutId="w-1", likesCount=2, commentsCount=1, isLiked=True)
        ]

        resp = await client.get("/api/social/workouts/meta?ids=w-1&ids=w-2")

    assert resp.status_code == 200
    assert resp.json()[0]["workoutId"] == "w-1"


# ── Like ──────────────────────────────────────────────────────────────────────

async def test_toggle_like(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.toggle_like.return_value = LikeStatusOut(isLiked=True, likesCount=5)

        resp = await client.post("/api/social/workouts/w-1/like")

    assert resp.status_code == 200
    assert resp.json()["isLiked"] is True
    svc.toggle_like.assert_called_once_with(1, "w-1")


# ── Comments ──────────────────────────────────────────────────────────────────

async def test_get_comments(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_comments.return_value = [_comment()]

        resp = await client.get("/api/social/workouts/w-1/comments")

    assert resp.status_code == 200
    assert len(resp.json()) == 1
    svc.get_comments.assert_called_once_with("w-1", 1)


async def test_add_comment(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.add_comment.return_value = _comment()

        resp = await client.post("/api/social/workouts/w-1/comments", json={"text": "Great workout!"})

    assert resp.status_code == 200
    assert resp.json()["text"] == "Great workout!"
    svc.add_comment.assert_called_once_with(1, "w-1", "Great workout!")


async def test_delete_comment(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.delete_comment.return_value = None

        resp = await client.delete("/api/social/workouts/w-1/comments/c-1")

    assert resp.status_code == 204
    svc.delete_comment.assert_called_once_with(1, "c-1")


async def test_delete_comment_not_found(client):
    with patch("app.api.routers.social.SocialService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.delete_comment.side_effect = HTTPException(404, "Комментарий не найден")

        resp = await client.delete("/api/social/workouts/w-1/comments/missing")

    assert resp.status_code == 404

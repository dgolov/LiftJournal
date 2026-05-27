from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.social import SocialRepository
from tests.conftest import scalar_result, scalars_result, make_user, make_workout


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.delete = AsyncMock()
    return db


def _scalar_count(n):
    r = MagicMock()
    r.scalar.return_value = n
    return r


def _make_follow(follower_id=1, following_id=2):
    f = MagicMock()
    f.follower_id = follower_id
    f.following_id = following_id
    return f


def _make_comment(id="c-1", user_id=1, workout_id="w-1", text="Nice"):
    c = MagicMock()
    c.id = id
    c.user_id = user_id
    c.workout_id = workout_id
    c.text = text
    from datetime import datetime
    c.created_at = datetime(2026, 1, 1)
    return c


def _make_like(user_id=1, workout_id="w-1"):
    l = MagicMock()
    l.user_id = user_id
    l.workout_id = workout_id
    return l


class TestSearchUsers:
    async def test_returns_matching_users(self, mock_db):
        users = [make_user(id=2, name="Alice")]
        mock_db.execute.return_value = scalars_result(users)

        result = await SocialRepository(mock_db).search_users("ali", current_user_id=1)

        assert result == users

    async def test_empty_when_no_match(self, mock_db):
        mock_db.execute.return_value = scalars_result([])

        result = await SocialRepository(mock_db).search_users("xyz", current_user_id=1)

        assert result == []


class TestGetUserById:
    async def test_found(self, mock_db):
        user = make_user(id=2)
        mock_db.execute.return_value = scalar_result(user)

        result = await SocialRepository(mock_db).get_user_by_id(2)

        assert result == user

    async def test_not_found(self, mock_db):
        mock_db.execute.return_value = scalar_result(None)

        result = await SocialRepository(mock_db).get_user_by_id(999)

        assert result is None


class TestCounts:
    async def test_followers_count(self, mock_db):
        mock_db.execute.return_value = _scalar_count(7)

        count = await SocialRepository(mock_db).followers_count(user_id=2)

        assert count == 7

    async def test_following_count(self, mock_db):
        mock_db.execute.return_value = _scalar_count(3)

        count = await SocialRepository(mock_db).following_count(user_id=2)

        assert count == 3

    async def test_workouts_count(self, mock_db):
        mock_db.execute.return_value = _scalar_count(15)

        count = await SocialRepository(mock_db).workouts_count(user_id=1)

        assert count == 15


class TestFollowUnfollow:
    async def test_is_following_true(self, mock_db):
        mock_db.execute.return_value = scalar_result(_make_follow())

        result = await SocialRepository(mock_db).is_following(follower_id=1, following_id=2)

        assert result is True

    async def test_is_following_false(self, mock_db):
        mock_db.execute.return_value = scalar_result(None)

        result = await SocialRepository(mock_db).is_following(follower_id=1, following_id=2)

        assert result is False

    async def test_follow_adds_when_not_following(self, mock_db):
        mock_db.execute.return_value = scalar_result(None)

        await SocialRepository(mock_db).follow(follower_id=1, following_id=2)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    async def test_follow_skips_when_already_following(self, mock_db):
        mock_db.execute.return_value = scalar_result(_make_follow())

        await SocialRepository(mock_db).follow(follower_id=1, following_id=2)

        mock_db.add.assert_not_called()

    async def test_unfollow_deletes(self, mock_db):
        follow = _make_follow()
        mock_db.execute.return_value = scalar_result(follow)

        await SocialRepository(mock_db).unfollow(follower_id=1, following_id=2)

        mock_db.delete.assert_called_once_with(follow)
        mock_db.commit.assert_called_once()

    async def test_unfollow_noop_when_not_following(self, mock_db):
        mock_db.execute.return_value = scalar_result(None)

        await SocialRepository(mock_db).unfollow(follower_id=1, following_id=2)

        mock_db.delete.assert_not_called()


class TestGetFollowers:
    async def test_returns_follower_users(self, mock_db):
        users = [make_user(id=3, name="Bob")]
        mock_db.execute.return_value = scalars_result(users)

        result = await SocialRepository(mock_db).get_followers(user_id=1)

        assert result == users

    async def test_returns_following_users(self, mock_db):
        users = [make_user(id=4, name="Carol")]
        mock_db.execute.return_value = scalars_result(users)

        result = await SocialRepository(mock_db).get_following(user_id=1)

        assert result == users


class TestLikes:
    async def test_toggle_like_adds_when_not_liked(self, mock_db):
        mock_db.execute.return_value = scalar_result(None)

        result = await SocialRepository(mock_db).toggle_like(user_id=1, workout_id="w-1")

        assert result is True
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    async def test_toggle_like_removes_when_liked(self, mock_db):
        like = _make_like()
        mock_db.execute.return_value = scalar_result(like)

        result = await SocialRepository(mock_db).toggle_like(user_id=1, workout_id="w-1")

        assert result is False
        mock_db.delete.assert_called_once_with(like)

    async def test_get_likes_count(self, mock_db):
        mock_db.execute.return_value = _scalar_count(4)

        count = await SocialRepository(mock_db).get_likes_count(workout_id="w-1")

        assert count == 4

    async def test_is_liked_true(self, mock_db):
        mock_db.execute.return_value = scalar_result(_make_like())

        result = await SocialRepository(mock_db).is_liked(user_id=1, workout_id="w-1")

        assert result is True

    async def test_is_liked_false(self, mock_db):
        mock_db.execute.return_value = scalar_result(None)

        result = await SocialRepository(mock_db).is_liked(user_id=1, workout_id="w-1")

        assert result is False

    async def test_get_likes_batch_empty(self, mock_db):
        result = await SocialRepository(mock_db).get_likes_batch([], user_id=1)

        assert result == {}
        mock_db.execute.assert_not_called()


class TestComments:
    async def test_add_comment(self, mock_db):
        comment = _make_comment()
        mock_db.refresh = AsyncMock()
        mock_db.add = MagicMock()

        # Simulate the add + commit + refresh flow
        repo = SocialRepository(mock_db)
        # Override refresh to set return value
        async def fake_refresh(obj):
            pass
        mock_db.refresh.side_effect = fake_refresh

        result = await repo.add_comment(user_id=1, workout_id="w-1", text="Nice")

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    async def test_delete_comment_found(self, mock_db):
        comment = _make_comment()
        mock_db.execute.return_value = scalar_result(comment)

        result = await SocialRepository(mock_db).delete_comment("c-1", user_id=1)

        assert result is True
        mock_db.delete.assert_called_once_with(comment)

    async def test_delete_comment_not_found(self, mock_db):
        mock_db.execute.return_value = scalar_result(None)

        result = await SocialRepository(mock_db).delete_comment("missing", user_id=1)

        assert result is False
        mock_db.delete.assert_not_called()

    async def test_get_comments_count_batch_empty(self, mock_db):
        result = await SocialRepository(mock_db).get_comments_count_batch([])

        assert result == {}
        mock_db.execute.assert_not_called()

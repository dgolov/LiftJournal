from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.services.social import SocialService

OWNER_ID = 2


def _workout():
    w = MagicMock()
    w.id = "w-1"
    w.user_id = OWNER_ID
    return w


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def repo():
    with patch("app.services.social.SocialRepository") as MockRepo:
        r = AsyncMock()
        MockRepo.return_value = r
        r.is_following.return_value = False
        r.toggle_like.return_value = True
        r.get_likes_count.return_value = 1
        r.get_comments.return_value = []
        yield r


@pytest.fixture
def coach_link():
    with patch("app.repositories.coach.CoachRepository") as MockCoachRepo:
        r = AsyncMock()
        MockCoachRepo.return_value = r
        r.get_active_link.return_value = None
        yield r


@pytest.fixture(autouse=True)
def notify():
    with patch("app.services.notifications.NotificationService") as MockNotify:
        MockNotify.return_value = AsyncMock()
        yield MockNotify


async def _like(mock_db, user_id):
    svc = SocialService(mock_db)
    with patch.object(SocialService, "_get_workout_model", AsyncMock(return_value=_workout())):
        return await svc.toggle_like(user_id, "w-1")


async def test_active_coach_can_like_without_following(mock_db, repo, coach_link):
    coach_link.get_active_link.return_value = MagicMock()

    result = await _like(mock_db, 1)

    assert result.isLiked is True
    coach_link.get_active_link.assert_called_once_with(1, OWNER_ID)


async def test_stranger_cannot_like(mock_db, repo, coach_link):
    with pytest.raises(HTTPException) as exc:
        await _like(mock_db, 1)

    assert exc.value.status_code == 403
    repo.toggle_like.assert_not_called()


async def test_follower_can_like_without_coach_lookup(mock_db, repo, coach_link):
    repo.is_following.return_value = True

    await _like(mock_db, 1)

    coach_link.get_active_link.assert_not_called()


async def test_active_coach_can_comment(mock_db, repo, coach_link):
    coach_link.get_active_link.return_value = MagicMock()
    coach = MagicMock(id=1)
    coach.name = "Coach"  # `name=` in the constructor would name the mock itself
    repo.get_user_by_id.return_value = coach
    repo.add_comment.return_value = MagicMock(id="c-1", text="Отлично", created_at=datetime(2026, 9, 28))

    svc = SocialService(mock_db)
    with patch.object(SocialService, "_get_workout_model", AsyncMock(return_value=_workout())):
        result = await svc.add_comment(1, "w-1", " Отлично ")

    assert result.text == "Отлично"
    repo.add_comment.assert_called_once_with(1, "w-1", "Отлично")


# ── Public profile: coaching extras ───────────────────────────────────────────

def _user(id, name, is_coach=False):
    u = MagicMock(id=id, avatar_url=None, is_coach=is_coach, coach_bio="", coach_accepting=False, birth_date=None)
    u.name = name
    return u


def _weight(kg):
    from datetime import date
    return MagicMock(date=date(2026, 9, 20), kg=kg)


async def _profile(mock_db, repo, coach_link, viewer_id, *, link=None):
    athlete, coach = _user(OWNER_ID, "Athlete"), _user(1, "Coach", is_coach=True)
    repo.get_user_by_id.return_value = athlete
    for m in ("followers_count", "following_count", "workouts_count"):
        getattr(repo, m).return_value = 0
    coach_link.get_open_link_between.return_value = None
    coach_link.list_links.return_value = [(MagicMock(), coach, athlete)]
    coach_link.get_active_link.return_value = link
    coach_link.get_weight_log.return_value = [_weight(81.0), _weight(82.5)]
    return await SocialService(mock_db).get_public_profile(OWNER_ID, viewer_id)


async def test_profile_lists_active_coach_for_everyone(mock_db, repo, coach_link):
    result = await _profile(mock_db, repo, coach_link, viewer_id=99)

    assert [c.name for c in result.coaches] == ["Coach"]
    assert result.currentWeight is None


async def test_coach_with_private_access_sees_current_weight(mock_db, repo, coach_link):
    result = await _profile(mock_db, repo, coach_link, viewer_id=1, link=MagicMock(can_see_private=True))

    assert result.currentWeight.kg == 82.5


async def test_coach_without_private_access_does_not_see_weight(mock_db, repo, coach_link):
    result = await _profile(mock_db, repo, coach_link, viewer_id=1, link=MagicMock(can_see_private=False))

    assert result.currentWeight is None

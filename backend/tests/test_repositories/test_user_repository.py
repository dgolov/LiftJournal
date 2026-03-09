from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.repositories.user import UserRepository
from tests.conftest import make_user, make_weight_entry, make_goal, make_user_max, scalar_result


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.delete = AsyncMock()
    return db


@pytest.fixture
def repo(mock_db):
    return UserRepository(mock_db)


# ---------------------------------------------------------------------------
# get_with_relations
# ---------------------------------------------------------------------------

async def test_get_with_relations_found(repo, mock_db):
    user = make_user(id=1)
    mock_db.execute.return_value = scalar_result(user)

    result = await repo.get_with_relations(1)

    assert result is user
    mock_db.execute.assert_called_once()


async def test_get_with_relations_not_found(repo, mock_db):
    mock_db.execute.return_value = scalar_result(None)

    result = await repo.get_with_relations(999)

    assert result is None


# ---------------------------------------------------------------------------
# get_by_email
# ---------------------------------------------------------------------------

async def test_get_by_email_found(repo, mock_db):
    user = make_user(email="test@test.com")
    mock_db.execute.return_value = scalar_result(user)

    result = await repo.get_by_email("test@test.com")

    assert result is user


async def test_get_by_email_not_found(repo, mock_db):
    mock_db.execute.return_value = scalar_result(None)

    result = await repo.get_by_email("nobody@test.com")

    assert result is None


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------

async def test_create_user_adds_and_commits(repo, mock_db):
    refreshed_user = make_user(id=1, email="new@test.com", name="New")
    mock_db.refresh.side_effect = lambda obj: None
    # After refresh, repo returns the object; simulate by pre-setting
    mock_db.refresh = AsyncMock()

    with patch("app.repositories.user.User") as MockUser:
        mock_instance = MagicMock()
        MockUser.return_value = mock_instance

        result = await repo.create(
            email="new@test.com",
            hashed_password="hashed",
            name="New",
        )

    mock_db.add.assert_called_once_with(mock_instance)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_instance)


# ---------------------------------------------------------------------------
# update_profile
# ---------------------------------------------------------------------------

async def test_update_profile_updates_fields(repo, mock_db):
    user = make_user(id=1, name="Old", age=20)
    updated_user = make_user(id=1, name="New", age=30)

    # First call: get_with_relations after update
    mock_db.execute.return_value = scalar_result(updated_user)

    result = await repo.update_profile(user, name="New", age=30, avatar_url=None)

    assert user.name == "New"
    assert user.age == 30
    mock_db.commit.assert_called_once()


async def test_update_profile_skips_none_fields(repo, mock_db):
    user = make_user(id=1, name="Keep", age=25, avatar_url="url")
    updated_user = make_user(id=1, name="Keep", age=25)
    mock_db.execute.return_value = scalar_result(updated_user)

    await repo.update_profile(user, name=None, age=None, avatar_url=None)

    # Fields should remain unchanged
    assert user.name == "Keep"
    assert user.age == 25


# ---------------------------------------------------------------------------
# upsert_weight
# ---------------------------------------------------------------------------

async def test_upsert_weight_creates_new_entry(repo, mock_db):
    # Return None → no existing entry → a new WeightEntry ORM object is created
    mock_db.execute.return_value = scalar_result(None)

    await repo.upsert_weight(1, date(2026, 3, 1), 80.0)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


async def test_upsert_weight_updates_existing_entry(repo, mock_db):
    existing = make_weight_entry(kg=75.0)
    mock_db.execute.return_value = scalar_result(existing)

    result = await repo.upsert_weight(1, date(2026, 3, 1), 80.0)

    assert existing.kg == 80.0
    mock_db.add.assert_not_called()
    mock_db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# delete_weight
# ---------------------------------------------------------------------------

async def test_delete_weight_existing(repo, mock_db):
    entry = make_weight_entry()
    mock_db.execute.return_value = scalar_result(entry)

    await repo.delete_weight(1, date(2026, 3, 1))

    mock_db.delete.assert_called_once_with(entry)
    mock_db.commit.assert_called_once()


async def test_delete_weight_not_found_does_nothing(repo, mock_db):
    mock_db.execute.return_value = scalar_result(None)

    await repo.delete_weight(1, date(2026, 3, 1))

    mock_db.delete.assert_not_called()
    mock_db.commit.assert_not_called()


# ---------------------------------------------------------------------------
# create_goal
# ---------------------------------------------------------------------------

async def test_create_goal_adds_and_commits(repo, mock_db):
    with patch("app.repositories.user.Goal") as MockGoal:
        goal_instance = MagicMock()
        MockGoal.return_value = goal_instance
        mock_db.refresh = AsyncMock()

        await repo.create_goal(1, "Run 5k", None, False)

    mock_db.add.assert_called_once_with(goal_instance)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(goal_instance)


# ---------------------------------------------------------------------------
# toggle_goal
# ---------------------------------------------------------------------------

async def test_toggle_goal_from_false_to_true(repo, mock_db):
    goal = make_goal(done=False)
    mock_db.execute.return_value = scalar_result(goal)

    result = await repo.toggle_goal(1, "goal-1")

    assert goal.done is True
    mock_db.commit.assert_called_once()
    assert result is goal


async def test_toggle_goal_from_true_to_false(repo, mock_db):
    goal = make_goal(done=True)
    mock_db.execute.return_value = scalar_result(goal)

    result = await repo.toggle_goal(1, "goal-1")

    assert goal.done is False


async def test_toggle_goal_not_found_returns_none(repo, mock_db):
    mock_db.execute.return_value = scalar_result(None)

    result = await repo.toggle_goal(1, "missing")

    assert result is None
    mock_db.commit.assert_not_called()


# ---------------------------------------------------------------------------
# delete_goal
# ---------------------------------------------------------------------------

async def test_delete_goal_existing(repo, mock_db):
    goal = make_goal()
    mock_db.execute.return_value = scalar_result(goal)

    await repo.delete_goal(1, "goal-1")

    mock_db.delete.assert_called_once_with(goal)
    mock_db.commit.assert_called_once()


async def test_delete_goal_not_found_does_nothing(repo, mock_db):
    mock_db.execute.return_value = scalar_result(None)

    await repo.delete_goal(1, "missing")

    mock_db.delete.assert_not_called()


# ---------------------------------------------------------------------------
# upsert_max
# ---------------------------------------------------------------------------

async def test_upsert_max_creates_new(repo, mock_db):
    # Return None → no existing max → a new UserMax ORM object is created
    mock_db.execute.return_value = scalar_result(None)
    mock_db.refresh = AsyncMock()

    await repo.upsert_max(1, "Bench Press", 100.0)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


async def test_upsert_max_updates_existing(repo, mock_db):
    existing = make_user_max(weight_kg=90.0)
    mock_db.execute.return_value = scalar_result(existing)
    mock_db.refresh = AsyncMock()

    await repo.upsert_max(1, "Bench Press", 100.0)

    assert existing.weight_kg == 100.0
    mock_db.add.assert_not_called()


# ---------------------------------------------------------------------------
# delete_max
# ---------------------------------------------------------------------------

async def test_delete_max_existing(repo, mock_db):
    m = make_user_max()
    mock_db.execute.return_value = scalar_result(m)

    await repo.delete_max(1, "Bench Press")

    mock_db.delete.assert_called_once_with(m)
    mock_db.commit.assert_called_once()


async def test_delete_max_not_found_does_nothing(repo, mock_db):
    mock_db.execute.return_value = scalar_result(None)

    await repo.delete_max(1, "Unknown")

    mock_db.delete.assert_not_called()

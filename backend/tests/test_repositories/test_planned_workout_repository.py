from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.planned_workout import PlannedWorkoutRepository
from tests.conftest import scalar_result, scalars_result


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.delete = AsyncMock()
    return db


def _make_plan(id="plan-1", user_id=1):
    plan = MagicMock()
    plan.id = id
    plan.user_id = user_id
    plan.title = "Силовая"
    plan.type = "Силовая"
    plan.scheduled_date = date(2026, 6, 1)
    plan.notes = ""
    plan.status = "planned"
    plan.completed_workout_id = None
    plan.created_at = datetime(2026, 1, 1)
    plan.exercises = []
    return plan


def _make_exercise_in(exercise_id="ex-1", name="Bench Press", sets=None):
    ex = MagicMock()
    ex.exerciseId = exercise_id
    ex.exerciseName = name
    ex.sets = sets or []
    return ex


class TestExpireOverdue:
    async def test_executes_update_and_commits(self, mock_db):
        await PlannedWorkoutRepository(mock_db).expire_overdue(user_id=1)

        mock_db.execute.assert_awaited_once()
        mock_db.commit.assert_called_once()


class TestGetAllByUser:
    async def test_returns_list(self, mock_db):
        plans = [_make_plan("p-1"), _make_plan("p-2")]
        mock_db.execute.return_value = scalars_result(plans)

        result = await PlannedWorkoutRepository(mock_db).get_all_by_user(user_id=1)

        assert result == plans

    async def test_empty(self, mock_db):
        mock_db.execute.return_value = scalars_result([])

        result = await PlannedWorkoutRepository(mock_db).get_all_by_user(user_id=1)

        assert result == []

    async def test_expires_overdue_before_listing(self, mock_db):
        """Overdue 'planned' entries must flip to 'skipped' before the list
        is read back, so a stale status never round-trips to the client."""
        mock_db.execute.return_value = scalars_result([])

        await PlannedWorkoutRepository(mock_db).get_all_by_user(user_id=1)

        assert mock_db.execute.await_count == 2
        assert mock_db.commit.call_count >= 1


class TestGetById:
    async def test_found(self, mock_db):
        plan = _make_plan()
        mock_db.execute.return_value = scalar_result(plan)

        result = await PlannedWorkoutRepository(mock_db).get_by_id("plan-1")

        assert result == plan

    async def test_not_found(self, mock_db):
        mock_db.execute.return_value = scalar_result(None)

        result = await PlannedWorkoutRepository(mock_db).get_by_id("missing")

        assert result is None


class TestCreate:
    async def test_adds_and_commits(self, mock_db):
        created = _make_plan()
        # get_by_id is called after insert: first execute for insert, second for get_by_id
        mock_db.execute.return_value = scalar_result(created)

        repo = PlannedWorkoutRepository(mock_db)
        result = await repo.create(
            user_id=1,
            title="Bench",
            type="Силовая",
            scheduled_date=date(2026, 6, 1),
            notes="",
            exercises_data=[],
        )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


class TestUpdate:
    async def test_updates_fields(self, mock_db):
        plan = _make_plan()
        updated = _make_plan()
        updated.title = "New Title"
        updated.status = "completed"
        mock_db.execute.return_value = scalar_result(updated)

        result = await PlannedWorkoutRepository(mock_db).update(
            plan, title="New Title", status="completed"
        )

        assert plan.title == "New Title"
        assert plan.status == "completed"
        mock_db.commit.assert_called_once()

    async def test_skips_none_fields(self, mock_db):
        plan = _make_plan()
        original_title = plan.title
        mock_db.execute.return_value = scalar_result(plan)

        await PlannedWorkoutRepository(mock_db).update(plan, title=None, type=None)

        assert plan.title == original_title


class TestDelete:
    async def test_deletes_and_commits(self, mock_db):
        plan = _make_plan()

        await PlannedWorkoutRepository(mock_db).delete(plan)

        mock_db.delete.assert_called_once_with(plan)
        mock_db.commit.assert_called_once()


class TestBuildExercises:
    def test_builds_exercise_with_sets(self):
        repo = PlannedWorkoutRepository(MagicMock())
        s = MagicMock()
        s.weight = 100.0
        s.reps = 5
        ex_in = _make_exercise_in(sets=[s])

        result = repo._build_exercises([ex_in])

        assert len(result) == 1
        assert result[0].exercise_id == "ex-1"
        assert result[0].exercise_name == "Bench Press"
        assert result[0].order == 0
        assert len(result[0].sets) == 1
        assert result[0].sets[0].weight == 100.0
        assert result[0].sets[0].reps == 5

    def test_empty_exercises(self):
        repo = PlannedWorkoutRepository(MagicMock())
        result = repo._build_exercises([])
        assert result == []

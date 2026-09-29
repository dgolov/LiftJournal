from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.api.schemas import PlannedWorkoutUpdate
from app.services.planned_workout import PlannedWorkoutService

ATHLETE_ID = 2
COACH_ID = 1


def make_plan(status="planned", created_by=COACH_ID, completed_workout_id=None):
    p = MagicMock()
    p.id = "plan-1"
    p.user_id = ATHLETE_ID
    p.title = "Присед"
    p.type = "Силовая"
    p.scheduled_date = date(2026, 10, 1)
    p.notes = ""
    p.status = status
    p.created_by = created_by
    p.creator = MagicMock()
    p.creator.name = "Coach"
    p.completed_workout_id = completed_workout_id
    p.cycle_id = None
    p.cycle_schedule_id = None
    p.cycle = None
    p.created_at = datetime(2026, 9, 1)
    p.exercises = []
    return p


@pytest.fixture
def mock_db():
    return AsyncMock()


async def _complete(mock_db, plan_before, *, link_active=True):
    with patch("app.services.planned_workout.PlannedWorkoutRepository") as MockRepo, \
            patch("app.repositories.coach.CoachRepository") as MockCoachRepo, \
            patch("app.services.notifications.NotificationService") as MockNotify:
        repo = AsyncMock()
        MockRepo.return_value = repo
        repo.get_by_id.return_value = plan_before
        repo.update.return_value = make_plan(
            status="completed", created_by=plan_before.created_by, completed_workout_id="w-1",
        )
        coach_repo = AsyncMock()
        MockCoachRepo.return_value = coach_repo
        coach_repo.get_active_link.return_value = MagicMock() if link_active else None
        notify = AsyncMock()
        MockNotify.return_value = notify

        result = await PlannedWorkoutService(mock_db).update(
            "plan-1", PlannedWorkoutUpdate(status="completed", completedWorkoutId="w-1"), ATHLETE_ID,
        )
    return result, notify


async def test_completing_coach_plan_notifies_coach(mock_db):
    result, notify = await _complete(mock_db, make_plan())

    notify.notify_athlete_completed.assert_called_once_with(
        athlete_id=ATHLETE_ID, coach_id=COACH_ID, planned_workout_id="plan-1", workout_id="w-1",
    )
    assert result.createdById == COACH_ID
    assert result.createdByName == "Coach"


async def test_completing_own_plan_does_not_notify(mock_db):
    result, notify = await _complete(mock_db, make_plan(created_by=ATHLETE_ID))

    notify.notify_athlete_completed.assert_not_called()
    assert result.createdById is None


async def test_completing_after_coaching_ended_does_not_notify(mock_db):
    _, notify = await _complete(mock_db, make_plan(), link_active=False)

    notify.notify_athlete_completed.assert_not_called()


async def test_re_saving_completed_plan_does_not_notify_again(mock_db):
    _, notify = await _complete(mock_db, make_plan(status="completed"))

    notify.notify_athlete_completed.assert_not_called()


@pytest.mark.parametrize("is_public,is_approved,created_by,visible", [
    (False, True, 1, True),      # own private cycle
    (True, True, 99, True),      # public approved
    (True, False, 99, False),    # public but pending moderation
    (False, True, 99, False),    # someone else's private cycle
])
async def test_check_cycle_visibility(mock_db, is_public, is_approved, created_by, visible):
    from fastapi import HTTPException
    cycle = MagicMock(is_public=is_public, is_approved=is_approved, created_by=created_by)
    with patch("app.services.planned_workout.PlannedWorkoutRepository"), \
            patch("app.repositories.cycle.CycleRepository") as MockCycles:
        cycles = AsyncMock()
        MockCycles.return_value = cycles
        cycles.get_by_id.return_value = cycle
        svc = PlannedWorkoutService(mock_db)
        if visible:
            await svc.check_cycle("c-1", 1)
        else:
            with pytest.raises(HTTPException) as exc:
                await svc.check_cycle("c-1", 1)
            assert exc.value.status_code == 404

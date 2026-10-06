from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.schemas import CoachLinkPermissionsUpdate, PlannedWorkoutCreate, PlannedWorkoutUpdate
from app.services.coach import CoachService
from tests.conftest import make_user

COACH_ID = 1
ATHLETE_ID = 2


def make_link(
    id="link-1", coach_id=COACH_ID, athlete_id=ATHLETE_ID, status="pending",
    initiated_by="coach", can_see_private=True, can_edit_plan=True, message="",
):
    link = MagicMock()
    link.id = id
    link.coach_id = coach_id
    link.athlete_id = athlete_id
    link.status = status
    link.initiated_by = initiated_by
    link.can_see_private = can_see_private
    link.can_edit_plan = can_edit_plan
    link.message = message
    link.created_at = datetime(2026, 9, 1)
    link.responded_at = None
    link.ended_at = None
    return link


def make_plan(id="plan-1", user_id=ATHLETE_ID, status="planned", title="Присед"):
    p = MagicMock()
    p.id = id
    p.user_id = user_id
    p.status = status
    p.title = title
    return p


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def repo():
    with patch("app.services.coach.CoachRepository") as MockRepo:
        r = AsyncMock()
        MockRepo.return_value = r
        users = {
            COACH_ID: make_user(id=COACH_ID, name="Coach", is_coach=True, coach_accepting=True),
            ATHLETE_ID: make_user(id=ATHLETE_ID, name="Athlete"),
        }
        r.get_user.side_effect = lambda uid: users.get(uid)
        r.save.side_effect = lambda link: link
        r.get_open_link.return_value = None
        r.is_following.return_value = True
        r.users = users
        yield r


@pytest.fixture
def notify():
    with patch("app.services.coach.NotificationService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        yield svc


# ── invite ────────────────────────────────────────────────────────────────────

async def test_invite_follower_creates_pending_link_and_notifies(mock_db, repo, notify):
    repo.create_link.return_value = make_link(message="Давай к старту")

    result = await CoachService(mock_db).invite(COACH_ID, ATHLETE_ID, "  Давай к старту ")

    repo.create_link.assert_called_once_with(
        coach_id=COACH_ID, athlete_id=ATHLETE_ID, initiated_by="coach", message="Давай к старту",
    )
    notify.notify_coach_invite.assert_called_once_with(COACH_ID, ATHLETE_ID, "link-1", "Давай к старту")
    assert result.status == "pending"
    assert result.coachName == "Coach"


async def test_invite_non_follower_rejected(mock_db, repo, notify):
    repo.is_following.return_value = False

    with pytest.raises(HTTPException) as exc:
        await CoachService(mock_db).invite(COACH_ID, ATHLETE_ID, "")

    assert exc.value.status_code == 400
    repo.is_following.assert_called_once_with(ATHLETE_ID, COACH_ID)
    repo.create_link.assert_not_called()


async def test_invite_requires_coach_role(mock_db, repo, notify):
    repo.users[COACH_ID].is_coach = False

    with pytest.raises(HTTPException) as exc:
        await CoachService(mock_db).invite(COACH_ID, ATHLETE_ID, "")

    assert exc.value.status_code == 403


async def test_invite_self_rejected(mock_db, repo, notify):
    with pytest.raises(HTTPException) as exc:
        await CoachService(mock_db).invite(COACH_ID, COACH_ID, "")

    assert exc.value.status_code == 400


async def test_invite_duplicate_open_link_rejected(mock_db, repo, notify):
    repo.get_open_link.return_value = make_link(status="active")

    with pytest.raises(HTTPException) as exc:
        await CoachService(mock_db).invite(COACH_ID, ATHLETE_ID, "")

    assert exc.value.status_code == 409
    repo.create_link.assert_not_called()


# ── request ───────────────────────────────────────────────────────────────────

async def test_request_to_open_coach_notifies_coach(mock_db, repo, notify):
    repo.create_link.return_value = make_link(initiated_by="athlete")

    result = await CoachService(mock_db).request(ATHLETE_ID, COACH_ID, "")

    repo.create_link.assert_called_once_with(
        coach_id=COACH_ID, athlete_id=ATHLETE_ID, initiated_by="athlete", message="",
    )
    notify.notify_coach_request.assert_called_once_with(ATHLETE_ID, COACH_ID, "link-1", "")
    assert result.initiatedBy == "athlete"


async def test_request_to_closed_coach_rejected(mock_db, repo, notify):
    repo.users[COACH_ID].coach_accepting = False

    with pytest.raises(HTTPException) as exc:
        await CoachService(mock_db).request(ATHLETE_ID, COACH_ID, "")

    assert exc.value.status_code == 400
    repo.create_link.assert_not_called()


async def test_request_to_non_coach_not_found(mock_db, repo, notify):
    repo.users[COACH_ID].is_coach = False

    with pytest.raises(HTTPException) as exc:
        await CoachService(mock_db).request(ATHLETE_ID, COACH_ID, "")

    assert exc.value.status_code == 404


async def test_request_duplicate_rejected(mock_db, repo, notify):
    repo.get_open_link.return_value = make_link(initiated_by="athlete")

    with pytest.raises(HTTPException) as exc:
        await CoachService(mock_db).request(ATHLETE_ID, COACH_ID, "")

    assert exc.value.status_code == 409


# ── accept / decline / cancel / end ───────────────────────────────────────────

async def test_athlete_accepts_coach_invite(mock_db, repo, notify):
    link = make_link(initiated_by="coach")
    repo.get_link.return_value = link

    result = await CoachService(mock_db).accept("link-1", ATHLETE_ID)

    assert link.status == "active"
    assert link.responded_at is not None
    notify.notify_coach_accepted.assert_called_once_with(ATHLETE_ID, COACH_ID, "link-1")
    assert result.status == "active"


async def test_coach_accepts_athlete_request(mock_db, repo, notify):
    link = make_link(initiated_by="athlete")
    repo.get_link.return_value = link

    await CoachService(mock_db).accept("link-1", COACH_ID)

    assert link.status == "active"
    notify.notify_coach_accepted.assert_called_once_with(COACH_ID, ATHLETE_ID, "link-1")


async def test_initiator_cannot_accept_own_invite(mock_db, repo, notify):
    repo.get_link.return_value = make_link(initiated_by="coach")

    with pytest.raises(HTTPException) as exc:
        await CoachService(mock_db).accept("link-1", COACH_ID)

    assert exc.value.status_code == 403


async def test_outsider_cannot_see_link(mock_db, repo, notify):
    repo.get_link.return_value = make_link()

    with pytest.raises(HTTPException) as exc:
        await CoachService(mock_db).accept("link-1", 99)

    assert exc.value.status_code == 404


async def test_accept_already_answered_conflict(mock_db, repo, notify):
    repo.get_link.return_value = make_link(status="declined")

    with pytest.raises(HTTPException) as exc:
        await CoachService(mock_db).accept("link-1", ATHLETE_ID)

    assert exc.value.status_code == 409


async def test_decline_does_not_notify(mock_db, repo, notify):
    link = make_link(initiated_by="coach")
    repo.get_link.return_value = link

    await CoachService(mock_db).decline("link-1", ATHLETE_ID)

    assert link.status == "declined"
    notify.notify_coach_accepted.assert_not_called()


async def test_initiator_cancels_pending(mock_db, repo, notify):
    link = make_link(initiated_by="coach")
    repo.get_link.return_value = link

    await CoachService(mock_db).cancel("link-1", COACH_ID)

    repo.delete.assert_called_once_with(link)


async def test_non_initiator_cannot_cancel(mock_db, repo, notify):
    repo.get_link.return_value = make_link(initiated_by="coach")

    with pytest.raises(HTTPException) as exc:
        await CoachService(mock_db).cancel("link-1", ATHLETE_ID)

    assert exc.value.status_code == 403
    repo.delete.assert_not_called()


@pytest.mark.parametrize("user_id", [COACH_ID, ATHLETE_ID])
async def test_either_side_can_end(mock_db, repo, notify, user_id):
    link = make_link(status="active")
    repo.get_link.return_value = link

    result = await CoachService(mock_db).end("link-1", user_id)

    assert link.status == "ended"
    assert link.ended_at is not None
    assert result.status == "ended"


async def test_end_inactive_conflict(mock_db, repo, notify):
    repo.get_link.return_value = make_link(status="pending")

    with pytest.raises(HTTPException) as exc:
        await CoachService(mock_db).end("link-1", COACH_ID)

    assert exc.value.status_code == 409


# ── permissions ───────────────────────────────────────────────────────────────

async def test_athlete_turns_off_plan_editing(mock_db, repo, notify):
    link = make_link(status="active")
    repo.get_link.return_value = link

    result = await CoachService(mock_db).update_permissions(
        "link-1", ATHLETE_ID, CoachLinkPermissionsUpdate(canEditPlan=False),
    )

    assert link.can_edit_plan is False
    assert link.can_see_private is True
    assert result.canEditPlan is False


async def test_coach_cannot_change_permissions(mock_db, repo, notify):
    repo.get_link.return_value = make_link(status="active")

    with pytest.raises(HTTPException) as exc:
        await CoachService(mock_db).update_permissions(
            "link-1", COACH_ID, CoachLinkPermissionsUpdate(canEditPlan=True),
        )

    assert exc.value.status_code == 403


# ── access to athlete data ────────────────────────────────────────────────────

async def test_no_active_link_hides_athlete_as_not_found(mock_db, repo, notify):
    repo.get_active_link.return_value = None

    with patch("app.services.coach.WorkoutService") as MockWorkouts:
        with pytest.raises(HTTPException) as exc:
            await CoachService(mock_db).get_athlete_workouts(COACH_ID, ATHLETE_ID, None, None)

    assert exc.value.status_code == 404
    MockWorkouts.assert_not_called()


async def test_active_link_returns_workouts_in_range(mock_db, repo, notify):
    repo.get_active_link.return_value = make_link(status="active")

    with patch("app.services.coach.WorkoutService") as MockWorkouts:
        svc = AsyncMock()
        MockWorkouts.return_value = svc
        svc.get_workouts.return_value = []

        await CoachService(mock_db).get_athlete_workouts(
            COACH_ID, ATHLETE_ID, date(2026, 9, 1), date(2026, 9, 30),
        )

    svc.get_workouts.assert_called_once_with(ATHLETE_ID, date_from=date(2026, 9, 1), date_to=date(2026, 9, 30))


async def test_private_data_hidden_without_permission(mock_db, repo, notify):
    repo.get_active_link.return_value = make_link(status="active", can_see_private=False)

    with pytest.raises(HTTPException) as exc:
        await CoachService(mock_db).get_athlete_maxes(COACH_ID, ATHLETE_ID)
    assert exc.value.status_code == 403

    with pytest.raises(HTTPException) as exc:
        await CoachService(mock_db).get_athlete_weight(COACH_ID, ATHLETE_ID)
    assert exc.value.status_code == 403


# ── planning for an athlete ───────────────────────────────────────────────────

def _plan_payload():
    return PlannedWorkoutCreate(title="Присед", scheduledDate=date(2026, 10, 1))


async def test_coach_creates_plan_with_authorship_and_notifies(mock_db, repo, notify):
    repo.get_active_link.return_value = make_link(status="active")

    with patch("app.services.coach.PlannedWorkoutRepository") as MockPlans, \
            patch("app.services.coach.PlannedWorkoutService") as MockPlanSvc:
        plans = AsyncMock()
        MockPlans.return_value = plans
        plans.create.return_value = make_plan()
        plan_svc = MagicMock()
        plan_svc.check_cycle = AsyncMock()
        MockPlanSvc.return_value = plan_svc

        await CoachService(mock_db).create_plan(COACH_ID, ATHLETE_ID, _plan_payload())

    kwargs = plans.create.call_args.kwargs
    assert kwargs["user_id"] == ATHLETE_ID
    assert kwargs["created_by"] == COACH_ID
    notify.notify_plan_assigned.assert_called_once_with(COACH_ID, ATHLETE_ID, "plan-1", "Присед")


async def test_plan_editing_forbidden_without_permission(mock_db, repo, notify):
    repo.get_active_link.return_value = make_link(status="active", can_edit_plan=False)

    with patch("app.services.coach.PlannedWorkoutRepository") as MockPlans:
        with pytest.raises(HTTPException) as exc:
            await CoachService(mock_db).create_plan(COACH_ID, ATHLETE_ID, _plan_payload())

    assert exc.value.status_code == 403
    MockPlans.assert_not_called()


async def test_plan_reading_allowed_without_edit_permission(mock_db, repo, notify):
    repo.get_active_link.return_value = make_link(status="active", can_edit_plan=False)

    with patch("app.services.coach.PlannedWorkoutRepository") as MockPlans, \
            patch("app.services.coach.PlannedWorkoutService"):
        plans = AsyncMock()
        MockPlans.return_value = plans
        plans.get_by_user_range.return_value = []

        result = await CoachService(mock_db).get_athlete_planned(COACH_ID, ATHLETE_ID, None, None)

    assert result == []


@pytest.mark.parametrize("status", ["completed", "skipped"])
async def test_coach_cannot_change_done_plan(mock_db, repo, notify, status):
    repo.get_active_link.return_value = make_link(status="active")

    with patch("app.services.coach.PlannedWorkoutRepository") as MockPlans:
        plans = AsyncMock()
        MockPlans.return_value = plans
        plans.get_by_id.return_value = make_plan(status=status)

        with pytest.raises(HTTPException) as exc:
            await CoachService(mock_db).update_plan(
                COACH_ID, ATHLETE_ID, "plan-1", PlannedWorkoutUpdate(title="x"),
            )
        assert exc.value.status_code == 409

        with pytest.raises(HTTPException) as exc:
            await CoachService(mock_db).delete_plan(COACH_ID, ATHLETE_ID, "plan-1")
        assert exc.value.status_code == 409

    plans.update.assert_not_called()
    plans.delete.assert_not_called()


async def test_coach_cannot_touch_someone_elses_plan(mock_db, repo, notify):
    repo.get_active_link.return_value = make_link(status="active")

    with patch("app.services.coach.PlannedWorkoutRepository") as MockPlans:
        plans = AsyncMock()
        MockPlans.return_value = plans
        plans.get_by_id.return_value = make_plan(user_id=99)

        with pytest.raises(HTTPException) as exc:
            await CoachService(mock_db).delete_plan(COACH_ID, ATHLETE_ID, "plan-1")

    assert exc.value.status_code == 404
    plans.delete.assert_not_called()


async def test_coach_cannot_link_plan_to_cycle_they_cannot_see(mock_db, repo, notify):
    repo.get_active_link.return_value = make_link(status="active")

    with patch("app.services.coach.PlannedWorkoutRepository") as MockPlans, \
            patch("app.services.coach.PlannedWorkoutService") as MockPlanSvc:
        plan_svc = MagicMock()
        plan_svc.check_cycle = AsyncMock(side_effect=HTTPException(404, "Цикл не найден"))
        MockPlanSvc.return_value = plan_svc

        with pytest.raises(HTTPException) as exc:
            await CoachService(mock_db).create_plan(
                COACH_ID, ATHLETE_ID,
                PlannedWorkoutCreate(title="T1", scheduledDate=date(2026, 10, 1), cycleId="foreign", cycleScheduleId="s-1"),
            )

    assert exc.value.status_code == 404
    plan_svc.check_cycle.assert_called_once_with("foreign", COACH_ID)
    MockPlans.return_value.create.assert_not_called()

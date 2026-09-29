from datetime import date, datetime
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from app.api.schemas import CoachLinkOut, AthleteSummaryOut


def _link(status="pending"):
    return CoachLinkOut(
        id="link-1", coachId=1, coachName="Coach", athleteId=2, athleteName="Athlete",
        status=status, initiatedBy="coach", canSeePrivate=True, canEditPlan=True,
        createdAt=datetime(2026, 9, 1),
    )


async def test_invite(client):
    with patch("app.api.routers.coach.CoachService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.invite.return_value = _link()

        resp = await client.post("/api/coach/invites", json={"athleteId": 2, "message": "Привет"})

    assert resp.status_code == 201
    svc.invite.assert_called_once_with(1, 2, "Привет")


async def test_request(client):
    with patch("app.api.routers.coach.CoachService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.request.return_value = _link()

        resp = await client.post("/api/coach/requests", json={"coachId": 5})

    assert resp.status_code == 201
    svc.request.assert_called_once_with(1, 5, "")


async def test_list_links_filters(client):
    with patch("app.api.routers.coach.CoachService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.list_links.return_value = [_link()]

        resp = await client.get("/api/coach/links?role=coach&status=pending&status=active")

    assert resp.status_code == 200
    svc.list_links.assert_called_once_with(1, "coach", ["pending", "active"])


async def test_list_links_rejects_unknown_role(client):
    resp = await client.get("/api/coach/links?role=admin")
    assert resp.status_code == 422


async def test_accept(client):
    with patch("app.api.routers.coach.CoachService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.accept.return_value = _link(status="active")

        resp = await client.post("/api/coach/links/link-1/accept")

    assert resp.status_code == 200
    assert resp.json()["status"] == "active"
    svc.accept.assert_called_once_with("link-1", 1)


async def test_cancel(client):
    with patch("app.api.routers.coach.CoachService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc

        resp = await client.delete("/api/coach/links/link-1")

    assert resp.status_code == 204
    svc.cancel.assert_called_once_with("link-1", 1)


async def test_athletes(client):
    with patch("app.api.routers.coach.CoachService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_athletes.return_value = [AthleteSummaryOut(
            linkId="link-1", id=2, name="Athlete", canSeePrivate=True, canEditPlan=True,
            weekPlanned=3, weekCompleted=2,
        )]

        resp = await client.get("/api/coach/athletes")

    assert resp.status_code == 200
    assert resp.json()[0]["weekCompleted"] == 2


async def test_athlete_workouts_passes_range(client):
    with patch("app.api.routers.coach.CoachService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_athlete_workouts.return_value = []

        resp = await client.get("/api/coach/athletes/2/workouts?from=2026-09-01&to=2026-09-30")

    assert resp.status_code == 200
    svc.get_athlete_workouts.assert_called_once_with(1, 2, date(2026, 9, 1), date(2026, 9, 30))


async def test_athlete_without_link_is_404(client):
    with patch("app.api.routers.coach.CoachService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.get_athlete_workouts.side_effect = HTTPException(404, "Подопечный не найден")

        resp = await client.get("/api/coach/athletes/2/workouts")

    assert resp.status_code == 404


async def test_create_athlete_plan(client):
    from app.api.schemas import PlannedWorkoutOut
    with patch("app.api.routers.coach.CoachService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.create_plan.return_value = PlannedWorkoutOut(
            id="plan-1", title="Присед", type="Силовая", scheduledDate=date(2026, 10, 1),
            notes="", status="planned", completedWorkoutId=None,
            createdAt=datetime(2026, 9, 1), exercises=[], createdById=1, createdByName="Coach",
        )

        resp = await client.post("/api/coach/athletes/2/planned", json={
            "title": "Присед", "scheduledDate": "2026-10-01",
        })

    assert resp.status_code == 201
    assert resp.json()["createdByName"] == "Coach"


async def test_update_coach_settings(client):
    from app.api.schemas import UserOut
    with patch("app.api.routers.users.UserService") as MockSvc:
        svc = AsyncMock()
        MockSvc.return_value = svc
        svc.update_coach_settings.return_value = UserOut(
            name="Coach", avatarUrl=None, isCoach=True, weightLog=[], goals=[],
        )

        resp = await client.patch("/api/user/coach", json={"isCoach": True})

    assert resp.status_code == 200
    assert resp.json()["isCoach"] is True

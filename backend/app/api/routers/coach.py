from datetime import date as DateType
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    CoachInviteIn, CoachRequestIn, CoachLinkOut, CoachLinkPermissionsUpdate,
    AthleteSummaryOut, PlannedWorkoutCreate, PlannedWorkoutUpdate, PlannedWorkoutOut,
    WorkoutOut, UserMaxOut, WeightEntryOut,
)
from app.core.database import get_db
from app.core.security import get_current_user
from app.domain.models import User
from app.services.coach import CoachService

router = APIRouter()


# ── Links ─────────────────────────────────────────────────────────────────────

@router.get("/links", response_model=list[CoachLinkOut])
async def list_links(
    role: Literal["coach", "athlete"] | None = Query(None),
    status: list[Literal["pending", "active", "declined", "ended"]] = Query(default=[]),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CoachService(db).list_links(current_user.id, role, list(status) or None)


@router.post("/invites", response_model=CoachLinkOut, status_code=201)
async def invite_athlete(
    payload: CoachInviteIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CoachService(db).invite(current_user.id, payload.athleteId, payload.message)


@router.post("/requests", response_model=CoachLinkOut, status_code=201)
async def request_coach(
    payload: CoachRequestIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CoachService(db).request(current_user.id, payload.coachId, payload.message)


@router.post("/links/{link_id}/accept", response_model=CoachLinkOut)
async def accept_link(
    link_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CoachService(db).accept(link_id, current_user.id)


@router.post("/links/{link_id}/decline", response_model=CoachLinkOut)
async def decline_link(
    link_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CoachService(db).decline(link_id, current_user.id)


@router.post("/links/{link_id}/end", response_model=CoachLinkOut)
async def end_link(
    link_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CoachService(db).end(link_id, current_user.id)


@router.patch("/links/{link_id}", response_model=CoachLinkOut)
async def update_link_permissions(
    link_id: str,
    payload: CoachLinkPermissionsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CoachService(db).update_permissions(link_id, current_user.id, payload)


@router.delete("/links/{link_id}", status_code=204)
async def cancel_link(
    link_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await CoachService(db).cancel(link_id, current_user.id)


# ── Athletes ──────────────────────────────────────────────────────────────────

@router.get("/athletes", response_model=list[AthleteSummaryOut])
async def list_athletes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CoachService(db).get_athletes(current_user.id)


@router.get("/athletes/{athlete_id}", response_model=AthleteSummaryOut)
async def get_athlete(
    athlete_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CoachService(db).get_athlete(current_user.id, athlete_id)


@router.get("/athletes/{athlete_id}/workouts", response_model=list[WorkoutOut])
async def get_athlete_workouts(
    athlete_id: int,
    from_: DateType | None = Query(None, alias="from"),
    to: DateType | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CoachService(db).get_athlete_workouts(current_user.id, athlete_id, from_, to)


@router.get("/athletes/{athlete_id}/planned", response_model=list[PlannedWorkoutOut])
async def get_athlete_planned(
    athlete_id: int,
    from_: DateType | None = Query(None, alias="from"),
    to: DateType | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CoachService(db).get_athlete_planned(current_user.id, athlete_id, from_, to)


@router.get("/athletes/{athlete_id}/maxes", response_model=list[UserMaxOut])
async def get_athlete_maxes(
    athlete_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CoachService(db).get_athlete_maxes(current_user.id, athlete_id)


@router.get("/athletes/{athlete_id}/weight", response_model=list[WeightEntryOut])
async def get_athlete_weight(
    athlete_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CoachService(db).get_athlete_weight(current_user.id, athlete_id)


@router.post("/athletes/{athlete_id}/planned", response_model=PlannedWorkoutOut, status_code=201)
async def create_athlete_plan(
    athlete_id: int,
    payload: PlannedWorkoutCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CoachService(db).create_plan(current_user.id, athlete_id, payload)


@router.patch("/athletes/{athlete_id}/planned/{plan_id}", response_model=PlannedWorkoutOut)
async def update_athlete_plan(
    athlete_id: int,
    plan_id: str,
    payload: PlannedWorkoutUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CoachService(db).update_plan(current_user.id, athlete_id, plan_id, payload)


@router.delete("/athletes/{athlete_id}/planned/{plan_id}", status_code=204)
async def delete_athlete_plan(
    athlete_id: int,
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await CoachService(db).delete_plan(current_user.id, athlete_id, plan_id)

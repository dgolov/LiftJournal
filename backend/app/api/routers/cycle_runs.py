from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import CycleRunOut, StartCycleWorkoutIn, CompleteWorkoutIn
from app.core.database import get_db
from app.core.security import get_current_user
from app.domain.models import User
from app.services.cycle_run import CycleRunService


router = APIRouter()


@router.get("/cycle-runs/active", response_model=CycleRunOut | None)
async def get_any_active_run(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CycleRunService(db).get_any_active_run(current_user.id)


@router.post("/cycles/{cycle_id}/start", response_model=CycleRunOut)
async def start_cycle(
    cycle_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CycleRunService(db).start_run(cycle_id, current_user.id)


@router.get("/cycles/{cycle_id}/run", response_model=CycleRunOut | None)
async def get_my_run(
    cycle_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CycleRunService(db).get_active_run(cycle_id, current_user.id)


@router.post("/cycle-runs/{run_id}/workouts/{cycle_workout_id}/start", response_model=dict)
async def start_cycle_workout(
    run_id: str,
    cycle_workout_id: str,
    body: StartCycleWorkoutIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CycleRunService(db).start_workout(run_id, cycle_workout_id, body.notes, current_user.id)


@router.post("/cycle-runs/{run_id}/workouts/{cycle_workout_id}/complete", response_model=CycleRunOut)
async def complete_cycle_workout(
    run_id: str,
    cycle_workout_id: str,
    body: CompleteWorkoutIn = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    workout_id = body.workout_id if body else None
    return await CycleRunService(db).complete_workout(run_id, cycle_workout_id, workout_id, current_user.id)


@router.post("/cycle-runs/{run_id}/finish", response_model=CycleRunOut)
async def finish_cycle_run(
    run_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CycleRunService(db).finish_run(run_id, current_user.id)

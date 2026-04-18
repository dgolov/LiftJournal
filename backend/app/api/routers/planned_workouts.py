from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import PlannedWorkoutCreate, PlannedWorkoutUpdate, PlannedWorkoutOut
from app.core.database import get_db
from app.core.security import get_current_user
from app.domain.models import User
from app.services.planned_workout import PlannedWorkoutService

router = APIRouter()


@router.get("", response_model=list[PlannedWorkoutOut])
async def list_planned(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await PlannedWorkoutService(db).get_all(current_user.id)


@router.post("", response_model=PlannedWorkoutOut, status_code=201)
async def create_planned(
    payload: PlannedWorkoutCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await PlannedWorkoutService(db).create(payload, current_user.id)


@router.patch("/{plan_id}", response_model=PlannedWorkoutOut)
async def update_planned(
    plan_id: str,
    payload: PlannedWorkoutUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await PlannedWorkoutService(db).update(plan_id, payload, current_user.id)


@router.delete("/{plan_id}", status_code=204)
async def delete_planned(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await PlannedWorkoutService(db).delete(plan_id, current_user.id)

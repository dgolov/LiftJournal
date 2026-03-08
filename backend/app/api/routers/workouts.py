from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import WorkoutCreate, WorkoutUpdate, WorkoutOut
from app.core.database import get_db
from app.core.security import get_current_user
from app.domain.models import User
from app.services.workout import WorkoutService

router = APIRouter()


@router.get("", response_model=list[WorkoutOut])
async def list_workouts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await WorkoutService(db).get_workouts(current_user.id)


@router.post("", response_model=WorkoutOut, status_code=201)
async def create_workout(
    payload: WorkoutCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await WorkoutService(db).create_workout(payload, current_user.id)


@router.get("/{workout_id}", response_model=WorkoutOut)
async def get_workout(
    workout_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await WorkoutService(db).get_workout(workout_id, current_user.id)


@router.patch("/{workout_id}", response_model=WorkoutOut)
async def update_workout(
    workout_id: str,
    payload: WorkoutUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await WorkoutService(db).update_workout(workout_id, payload, current_user.id)


@router.delete("/{workout_id}", status_code=204)
async def delete_workout(
    workout_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await WorkoutService(db).delete_workout(workout_id, current_user.id)

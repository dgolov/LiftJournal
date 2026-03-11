from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    ProfileUpdate, WeightEntryIn, WeightEntryOut,
    GoalCreate, GoalOut, UserOut, UserMaxIn, UserMaxOut,
)
from app.core.database import get_db
from app.core.security import get_current_user
from app.domain.models import User
from app.services.user import UserService


router = APIRouter()


@router.get("", response_model=UserOut)
async def get_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await UserService(db).get_user(current_user.id)


@router.patch("/profile", response_model=UserOut)
async def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await UserService(db).update_profile(current_user.id, payload)


@router.post("/weight", response_model=WeightEntryOut)
async def log_weight(
    payload: WeightEntryIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await UserService(db).log_weight(current_user.id, payload)


@router.delete("/weight/{entry_date}", status_code=204)
async def delete_weight(
    entry_date: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await UserService(db).delete_weight(current_user.id, entry_date)


@router.post("/goals", response_model=GoalOut, status_code=201)
async def create_goal(
    payload: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await UserService(db).create_goal(current_user.id, payload)


@router.patch("/goals/{goal_id}/toggle", response_model=GoalOut)
async def toggle_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await UserService(db).toggle_goal(current_user.id, goal_id)


@router.delete("/goals/{goal_id}", status_code=204)
async def delete_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await UserService(db).delete_goal(current_user.id, goal_id)


@router.post("/maxes", response_model=UserMaxOut)
async def upsert_max(
    payload: UserMaxIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await UserService(db).upsert_max(current_user.id, payload)


@router.delete("/maxes/{exercise_name}", status_code=204)
async def delete_max(
    exercise_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await UserService(db).delete_max(current_user.id, exercise_name)

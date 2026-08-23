from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import AdminUserOut, AdminExerciseOut, AdminExerciseUpdate, AdminCycleOut
from app.core.database import get_db
from app.core.security import get_current_admin
from app.domain.models import User
from app.services.admin import AdminService

router = APIRouter()


@router.get("/users", response_model=list[AdminUserOut])
async def list_users(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return await AdminService(db).list_users()


@router.get("/exercises", response_model=list[AdminExerciseOut])
async def list_exercises(
    status: str = Query("pending", pattern="^(pending|approved|private|rejected|all)$"),
    search: str | None = None,
    muscleGroup: str | None = None,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return await AdminService(db).list_exercises(status, search, muscleGroup)


@router.post("/exercises/{exercise_id}/approve", response_model=AdminExerciseOut)
async def approve_exercise(
    exercise_id: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return await AdminService(db).approve_exercise(exercise_id)


@router.post("/exercises/{exercise_id}/revoke", response_model=AdminExerciseOut)
async def revoke_exercise(
    exercise_id: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return await AdminService(db).revoke_exercise(exercise_id)


@router.patch("/exercises/{exercise_id}", response_model=AdminExerciseOut)
async def rename_exercise(
    exercise_id: str,
    payload: AdminExerciseUpdate,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return await AdminService(db).rename_exercise(exercise_id, payload.name)


@router.delete("/exercises/{exercise_id}", status_code=204)
async def reject_exercise(
    exercise_id: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    await AdminService(db).reject_exercise(exercise_id)


@router.get("/cycles", response_model=list[AdminCycleOut])
async def list_cycles(
    status: str = Query("pending", pattern="^(pending|all)$"),
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return await AdminService(db).list_cycles(status)


@router.post("/cycles/{cycle_id}/approve", response_model=AdminCycleOut)
async def approve_cycle(
    cycle_id: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return await AdminService(db).approve_cycle(cycle_id)


@router.post("/cycles/{cycle_id}/revoke", response_model=AdminCycleOut)
async def revoke_cycle(
    cycle_id: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return await AdminService(db).revoke_cycle(cycle_id)


@router.delete("/cycles/{cycle_id}", status_code=204)
async def reject_cycle(
    cycle_id: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    await AdminService(db).reject_cycle(cycle_id)

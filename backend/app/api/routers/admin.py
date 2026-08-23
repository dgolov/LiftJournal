from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import AdminUserOut, AdminExerciseOut
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


@router.get("/exercises/pending", response_model=list[AdminExerciseOut])
async def list_pending_exercises(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return await AdminService(db).list_pending_exercises()


@router.post("/exercises/{exercise_id}/approve", response_model=AdminExerciseOut)
async def approve_exercise(
    exercise_id: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return await AdminService(db).approve_exercise(exercise_id)


@router.delete("/exercises/{exercise_id}", status_code=204)
async def reject_exercise(
    exercise_id: str,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    await AdminService(db).reject_exercise(exercise_id)

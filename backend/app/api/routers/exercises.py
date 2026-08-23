from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import ExerciseCreate, ExerciseOut
from app.core.database import get_db
from app.core.security import get_current_user
from app.domain.models import User
from app.services.exercise import ExerciseService


router = APIRouter()


@router.get("", response_model=list[ExerciseOut])
async def list_exercises(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ExerciseService(db).list_exercises(current_user.id)


@router.post("", response_model=ExerciseOut, status_code=201)
async def create_exercise(
    payload: ExerciseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ExerciseService(db).create_custom(payload, current_user.id)

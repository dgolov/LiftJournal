from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import ExerciseCreate, ExerciseOut
from app.core.database import get_db
from app.services.exercise import ExerciseService


router = APIRouter()


@router.get("", response_model=list[ExerciseOut])
async def list_exercises(db: AsyncSession = Depends(get_db)):
    return await ExerciseService(db).list_exercises()


@router.post("", response_model=ExerciseOut, status_code=201)
async def create_exercise(payload: ExerciseCreate, db: AsyncSession = Depends(get_db)):
    return await ExerciseService(db).create_custom(payload)

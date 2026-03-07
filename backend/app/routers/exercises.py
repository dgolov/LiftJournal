from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.db.models import Exercise
from app.schemas import ExerciseCreate, ExerciseOut

router = APIRouter()


def _serialize(e: Exercise) -> ExerciseOut:
    return ExerciseOut(
        id=e.id,
        name=e.name,
        muscleGroup=e.muscle_group,
        secondaryMuscles=e.secondary_muscles or [],
        equipment=e.equipment,
        description=e.description or "",
        isCustom=e.is_custom,
    )


@router.get("", response_model=list[ExerciseOut])
async def list_exercises(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Exercise).order_by(Exercise.name))
    return [_serialize(e) for e in result.scalars().all()]


@router.post("", response_model=ExerciseOut, status_code=201)
async def create_exercise(payload: ExerciseCreate, db: AsyncSession = Depends(get_db)):
    e = Exercise(
        name=payload.name,
        muscle_group=payload.muscleGroup,
        secondary_muscles=payload.secondaryMuscles,
        equipment=payload.equipment,
        description=payload.description,
        is_custom=True,
    )
    db.add(e)
    await db.commit()
    await db.refresh(e)
    return _serialize(e)

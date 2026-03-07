from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.db.models import Workout, WorkoutExercise, ExerciseSet
from app.schemas import WorkoutCreate, WorkoutUpdate, WorkoutOut, WorkoutExerciseOut, SetOut

router = APIRouter()


def _serialize(w: Workout) -> WorkoutOut:
    return WorkoutOut(
        id=w.id,
        date=w.date,
        type=w.type,
        title=w.title,
        durationMinutes=w.duration_minutes,
        notes=w.notes or "",
        createdAt=w.created_at,
        exercises=[
            WorkoutExerciseOut(
                exerciseId=we.exercise_id,
                exerciseName=we.exercise_name,
                sets=[
                    SetOut(id=s.id, weight=s.weight, reps=s.reps, completed=s.completed)
                    for s in we.sets
                ],
            )
            for we in w.exercises
        ],
    )


def _with_exercises():
    return selectinload(Workout.exercises).selectinload(WorkoutExercise.sets)


async def _get_or_404(db: AsyncSession, workout_id: str) -> Workout:
    result = await db.execute(
        select(Workout).options(_with_exercises()).where(Workout.id == workout_id)
    )
    w = result.scalar_one_or_none()
    if not w:
        raise HTTPException(status_code=404, detail="Workout not found")
    return w


def _build_exercises(data: WorkoutCreate | WorkoutUpdate) -> list[WorkoutExercise]:
    exercises = []
    for i, ex_in in enumerate(data.exercises or []):
        we = WorkoutExercise(
            exercise_id=ex_in.exerciseId,
            exercise_name=ex_in.exerciseName,
            order=i,
        )
        we.sets = [
            ExerciseSet(weight=s.weight, reps=s.reps, completed=s.completed, order=j)
            for j, s in enumerate(ex_in.sets)
        ]
        exercises.append(we)
    return exercises


@router.get("", response_model=list[WorkoutOut])
async def list_workouts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Workout)
        .options(_with_exercises())
        .order_by(Workout.created_at.desc())
    )
    workouts = result.scalars().all()
    return [_serialize(w) for w in workouts]


@router.post("", response_model=WorkoutOut, status_code=201)
async def create_workout(payload: WorkoutCreate, db: AsyncSession = Depends(get_db)):
    w = Workout(
        date=payload.date,
        type=payload.type,
        title=payload.title,
        duration_minutes=payload.durationMinutes,
        notes=payload.notes,
        created_at=datetime.utcnow(),
    )
    w.exercises = _build_exercises(payload)
    db.add(w)
    await db.commit()
    await db.refresh(w)
    result = await db.execute(
        select(Workout).options(_with_exercises()).where(Workout.id == w.id)
    )
    return _serialize(result.scalar_one())


@router.get("/{workout_id}", response_model=WorkoutOut)
async def get_workout(workout_id: str, db: AsyncSession = Depends(get_db)):
    return _serialize(await _get_or_404(db, workout_id))


@router.patch("/{workout_id}", response_model=WorkoutOut)
async def update_workout(
    workout_id: str, payload: WorkoutUpdate, db: AsyncSession = Depends(get_db)
):
    w = await _get_or_404(db, workout_id)

    if payload.date is not None:
        w.date = payload.date
    if payload.type is not None:
        w.type = payload.type
    if payload.title is not None:
        w.title = payload.title
    if payload.durationMinutes is not None:
        w.duration_minutes = payload.durationMinutes
    if payload.notes is not None:
        w.notes = payload.notes
    if payload.exercises is not None:
        w.exercises = _build_exercises(payload)

    await db.commit()
    result = await db.execute(
        select(Workout).options(_with_exercises()).where(Workout.id == w.id)
    )
    return _serialize(result.scalar_one())


@router.delete("/{workout_id}", status_code=204)
async def delete_workout(workout_id: str, db: AsyncSession = Depends(get_db)):
    w = await _get_or_404(db, workout_id)
    await db.delete(w)
    await db.commit()

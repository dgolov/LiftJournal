from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user
from app.database import get_db
from app.db.models import TrainingCycle, CycleWorkout, CycleExercise, CycleSet, User
from app.schemas import CycleCreate, CycleUpdate, CycleListOut, CycleDetailOut, CycleWorkoutOut, CycleExerciseOut, CycleSetOut

router = APIRouter()


def _load_full():
    return selectinload(TrainingCycle.workouts).selectinload(CycleWorkout.exercises).selectinload(CycleExercise.sets)


def _serialize_detail(c: TrainingCycle) -> CycleDetailOut:
    return CycleDetailOut(
        id=c.id,
        title=c.title,
        description=c.description or "",
        author_name=c.author_name or "",
        created_by=c.created_by,
        is_public=c.is_public,
        created_at=c.created_at,
        workouts=[
            CycleWorkoutOut(
                id=w.id,
                workout_number=w.workout_number,
                title=w.title or "",
                notes=w.notes or "",
                exercises=[
                    CycleExerciseOut(
                        id=e.id,
                        exercise_name=e.exercise_name,
                        sets=[
                            CycleSetOut(id=s.id, percent_1rm=s.percent_1rm, reps=s.reps, order=s.order)
                            for s in e.sets
                        ],
                    )
                    for e in w.exercises
                ],
            )
            for w in c.workouts
        ],
    )


def _build_workouts(workouts_in) -> list[CycleWorkout]:
    result = []
    for i, w_in in enumerate(workouts_in or []):
        w = CycleWorkout(workout_number=w_in.workout_number, title=w_in.title, notes=w_in.notes, order=i)
        for j, e_in in enumerate(w_in.exercises):
            e = CycleExercise(exercise_name=e_in.exercise_name, order=j)
            e.sets = [
                CycleSet(percent_1rm=s.percent_1rm, reps=s.reps, order=k)
                for k, s in enumerate(e_in.sets)
            ]
            w.exercises.append(e)
        result.append(w)
    return result


async def _get_or_404(db: AsyncSession, cycle_id: str) -> TrainingCycle:
    result = await db.execute(select(TrainingCycle).options(_load_full()).where(TrainingCycle.id == cycle_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Цикл не найден")
    return c


@router.get("", response_model=list[CycleListOut])
async def list_cycles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Public cycles + current user's own cycles."""
    result = await db.execute(
        select(TrainingCycle).where(
            (TrainingCycle.is_public == True) | (TrainingCycle.created_by == current_user.id)  # noqa: E712
        ).order_by(TrainingCycle.created_at.desc())
    )
    cycles = result.scalars().all()

    # Count workouts for each cycle
    count_result = await db.execute(
        select(CycleWorkout.cycle_id, func.count(CycleWorkout.id).label("cnt"))
        .group_by(CycleWorkout.cycle_id)
    )
    counts = {row.cycle_id: row.cnt for row in count_result}

    return [
        CycleListOut(
            id=c.id,
            title=c.title,
            description=c.description or "",
            author_name=c.author_name or "",
            created_by=c.created_by,
            is_public=c.is_public,
            created_at=c.created_at,
            workout_count=counts.get(c.id, 0),
        )
        for c in cycles
    ]


@router.get("/{cycle_id}", response_model=CycleDetailOut)
async def get_cycle(
    cycle_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    c = await _get_or_404(db, cycle_id)
    if not c.is_public and c.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    return _serialize_detail(c)


@router.post("", response_model=CycleDetailOut, status_code=201)
async def create_cycle(
    payload: CycleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    c = TrainingCycle(
        created_by=current_user.id,
        title=payload.title,
        description=payload.description,
        author_name=payload.author_name,
        is_public=payload.is_public,
        created_at=datetime.utcnow(),
    )
    c.workouts = _build_workouts(payload.workouts)
    db.add(c)
    await db.commit()

    result = await db.execute(select(TrainingCycle).options(_load_full()).where(TrainingCycle.id == c.id))
    return _serialize_detail(result.scalar_one())


@router.patch("/{cycle_id}", response_model=CycleDetailOut)
async def update_cycle(
    cycle_id: str,
    payload: CycleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    c = await _get_or_404(db, cycle_id)
    if c.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа")

    if payload.title is not None:
        c.title = payload.title
    if payload.description is not None:
        c.description = payload.description
    if payload.author_name is not None:
        c.author_name = payload.author_name
    if payload.is_public is not None:
        c.is_public = payload.is_public
    if payload.workouts is not None:
        c.workouts = _build_workouts(payload.workouts)

    await db.commit()
    result = await db.execute(select(TrainingCycle).options(_load_full()).where(TrainingCycle.id == c.id))
    return _serialize_detail(result.scalar_one())


@router.delete("/{cycle_id}", status_code=204)
async def delete_cycle(
    cycle_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    c = await _get_or_404(db, cycle_id)
    if c.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    await db.delete(c)
    await db.commit()

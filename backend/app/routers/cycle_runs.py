from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import get_current_user
from app.database import get_db
from app.db.models import (
    UserCycleRun, CycleWorkoutLog, TrainingCycle, CycleWorkout,
    Workout, WorkoutExercise, ExerciseSet, User, UserMax, gen_uuid
)
from app.schemas import CycleRunOut, CycleWorkoutLogOut, StartCycleWorkoutIn, CompleteWorkoutIn, WorkoutOut, WorkoutExerciseOut, SetOut

router = APIRouter()


def _serialize_run(run: UserCycleRun) -> CycleRunOut:
    return CycleRunOut(
        id=run.id,
        cycle_id=run.cycle_id,
        started_at=run.started_at,
        logs=[
            CycleWorkoutLogOut(
                id=log.id,
                cycle_workout_id=log.cycle_workout_id,
                workout_id=log.workout_id,
                completed_at=log.completed_at,
            )
            for log in run.logs
        ],
    )


def _serialize_workout(w: Workout) -> WorkoutOut:
    return WorkoutOut(
        id=w.id,
        date=w.date,
        type=w.type,
        title=w.title,
        durationMinutes=w.duration_minutes,
        notes=w.notes,
        createdAt=w.created_at,
        exercises=[
            WorkoutExerciseOut(
                exerciseId=ex.exercise_id,
                exerciseName=ex.exercise_name,
                sets=[
                    SetOut(id=s.id, weight=s.weight, reps=s.reps, completed=s.completed)
                    for s in ex.sets
                ],
            )
            for ex in w.exercises
        ],
    )


def _round_to_2_5(kg: float) -> float:
    return round(kg / 2.5) * 2.5


async def _get_run(db: AsyncSession, run_id: str, user_id: int) -> UserCycleRun:
    result = await db.execute(
        select(UserCycleRun)
        .options(selectinload(UserCycleRun.logs))
        .where(UserCycleRun.id == run_id, UserCycleRun.user_id == user_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Прогон цикла не найден")
    return run


@router.post("/cycles/{cycle_id}/start", response_model=CycleRunOut)
async def start_cycle(
    cycle_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start a cycle run (idempotent — returns existing active run if already started)."""
    # Check cycle exists and is accessible
    result = await db.execute(select(TrainingCycle).where(TrainingCycle.id == cycle_id))
    cycle = result.scalar_one_or_none()
    if not cycle:
        raise HTTPException(status_code=404, detail="Цикл не найден")
    if not cycle.is_public and cycle.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Нет доступа")

    # Return existing run if present
    existing = await db.execute(
        select(UserCycleRun)
        .options(selectinload(UserCycleRun.logs))
        .where(UserCycleRun.user_id == current_user.id, UserCycleRun.cycle_id == cycle_id)
    )
    run = existing.scalar_one_or_none()
    if run:
        return _serialize_run(run)

    run = UserCycleRun(user_id=current_user.id, cycle_id=cycle_id, started_at=datetime.utcnow())
    db.add(run)
    await db.commit()
    await db.refresh(run)

    result2 = await db.execute(
        select(UserCycleRun).options(selectinload(UserCycleRun.logs)).where(UserCycleRun.id == run.id)
    )
    return _serialize_run(result2.scalar_one())


@router.get("/cycles/{cycle_id}/run", response_model=CycleRunOut | None)
async def get_my_run(
    cycle_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's run for this cycle, or null if not started."""
    result = await db.execute(
        select(UserCycleRun)
        .options(selectinload(UserCycleRun.logs))
        .where(UserCycleRun.user_id == current_user.id, UserCycleRun.cycle_id == cycle_id)
    )
    run = result.scalar_one_or_none()
    return _serialize_run(run) if run else None


@router.post("/cycle-runs/{run_id}/workouts/{cycle_workout_id}/start", response_model=dict)
async def start_cycle_workout(
    run_id: str,
    cycle_workout_id: str,
    body: StartCycleWorkoutIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a pre-filled workout from cycle workout. Idempotent — returns existing if already started."""
    run = await _get_run(db, run_id, current_user.id)

    # Check if log already exists for this cycle workout
    existing_log = next((l for l in run.logs if l.cycle_workout_id == cycle_workout_id), None)
    if existing_log and existing_log.workout_id:
        return {"run_id": run.id, "log_id": existing_log.id, "workout_id": existing_log.workout_id}

    # Load cycle workout with exercises and sets
    from app.db.models import CycleExercise
    result = await db.execute(
        select(CycleWorkout)
        .options(selectinload(CycleWorkout.exercises).selectinload(CycleExercise.sets))
        .where(CycleWorkout.id == cycle_workout_id)
    )
    cycle_workout = result.scalar_one_or_none()
    if not cycle_workout or cycle_workout.cycle_id != run.cycle_id:
        raise HTTPException(status_code=404, detail="Тренировка цикла не найдена")

    # Load user maxes for weight calculation
    maxes_result = await db.execute(
        select(UserMax).where(UserMax.user_id == current_user.id)
    )
    maxes = {m.exercise_name: m.weight_kg for m in maxes_result.scalars().all()}

    # Get cycle title for workout name
    cycle_result = await db.execute(select(TrainingCycle).where(TrainingCycle.id == run.cycle_id))
    cycle = cycle_result.scalar_one()

    # Build workout
    workout = Workout(
        user_id=current_user.id,
        date=date.today(),
        type="Силовая",
        title=f"Тренировка {cycle_workout.workout_number} — {cycle.title}",
        notes=body.notes,
        duration_minutes=0,
        created_at=datetime.utcnow(),
    )
    db.add(workout)
    await db.flush()  # get workout.id

    for order, ex in enumerate(sorted(cycle_workout.exercises, key=lambda e: e.order)):
        max_kg = maxes.get(ex.exercise_name)
        we = WorkoutExercise(
            workout_id=workout.id,
            exercise_id=gen_uuid(),  # synthetic id since no exercises table reference
            exercise_name=ex.exercise_name,
            order=order,
        )
        db.add(we)
        await db.flush()

        for s_order, s in enumerate(sorted(ex.sets, key=lambda x: x.order)):
            weight = _round_to_2_5(max_kg * s.percent_1rm / 100) if max_kg else 0.0
            es = ExerciseSet(
                workout_exercise_id=we.id,
                weight=weight,
                reps=s.reps,
                completed=False,
                order=s_order,
            )
            db.add(es)

    # Create or update log entry
    if existing_log:
        existing_log.workout_id = workout.id
        log = existing_log
    else:
        log = CycleWorkoutLog(
            run_id=run.id,
            cycle_workout_id=cycle_workout_id,
            workout_id=workout.id,
        )
        db.add(log)

    await db.commit()
    return {"run_id": run.id, "log_id": log.id, "workout_id": workout.id}


@router.post("/cycle-runs/{run_id}/workouts/{cycle_workout_id}/complete", response_model=CycleRunOut)
async def complete_cycle_workout(
    run_id: str,
    cycle_workout_id: str,
    body: CompleteWorkoutIn = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a cycle workout as completed. Creates log entry if not exists."""
    run = await _get_run(db, run_id, current_user.id)
    log = next((l for l in run.logs if l.cycle_workout_id == cycle_workout_id), None)
    if log:
        if body and body.workout_id:
            log.workout_id = body.workout_id
    else:
        log = CycleWorkoutLog(
            run_id=run_id,
            cycle_workout_id=cycle_workout_id,
            workout_id=body.workout_id if body else None,
        )
        db.add(log)
    log.completed_at = datetime.utcnow()
    await db.commit()

    result = await db.execute(
        select(UserCycleRun).options(selectinload(UserCycleRun.logs)).where(UserCycleRun.id == run_id)
    )
    return _serialize_run(result.scalar_one())

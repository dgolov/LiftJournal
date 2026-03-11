from datetime import datetime, date

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import (
    UserCycleRun, CycleWorkoutLog, CycleWorkout, CycleExercise,
    TrainingCycle, Workout, WorkoutExercise, ExerciseSet, UserMax, gen_uuid,
)


class CycleRunRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_active_run(self, user_id: int, cycle_id: str) -> UserCycleRun | None:
        result = await self.db.execute(
            select(UserCycleRun)
            .options(selectinload(UserCycleRun.logs))
            .where(
                UserCycleRun.user_id == user_id,
                UserCycleRun.cycle_id == cycle_id,
                UserCycleRun.completed_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_run_by_id(self, run_id: str, user_id: int) -> UserCycleRun | None:
        result = await self.db.execute(
            select(UserCycleRun)
            .options(selectinload(UserCycleRun.logs))
            .where(UserCycleRun.id == run_id, UserCycleRun.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_run(self, user_id: int, cycle_id: str) -> UserCycleRun:
        run = UserCycleRun(user_id=user_id, cycle_id=cycle_id, started_at=datetime.utcnow())
        self.db.add(run)
        await self.db.commit()
        return await self.get_run_by_id(run.id, user_id)  # type: ignore[return-value]

    async def get_cycle_workout(self, cycle_workout_id: str) -> CycleWorkout | None:
        result = await self.db.execute(
            select(CycleWorkout)
            .options(selectinload(CycleWorkout.exercises).selectinload(CycleExercise.sets))
            .where(CycleWorkout.id == cycle_workout_id)
        )
        return result.scalar_one_or_none()

    async def get_cycle(self, cycle_id: str) -> TrainingCycle | None:
        result = await self.db.execute(select(TrainingCycle).where(TrainingCycle.id == cycle_id))
        return result.scalar_one_or_none()

    async def get_user_maxes(self, user_id: int) -> dict[str, float]:
        result = await self.db.execute(select(UserMax).where(UserMax.user_id == user_id))
        return {m.exercise_name: m.weight_kg for m in result.scalars().all()}

    async def create_prefilled_workout(
        self,
        run: UserCycleRun,
        cycle_workout: CycleWorkout,
        cycle_title: str,
        notes: str,
        maxes: dict[str, float],
    ) -> tuple[Workout, CycleWorkoutLog]:
        workout = Workout(
            user_id=run.user_id,
            date=date.today(),
            type="Силовая",
            title=f"Тренировка {cycle_workout.workout_number} — {cycle_title}",
            notes=notes,
            duration_minutes=0,
            created_at=datetime.utcnow(),
        )
        self.db.add(workout)
        await self.db.flush()

        for order, ex in enumerate(sorted(cycle_workout.exercises, key=lambda e: e.order)):
            max_kg = maxes.get(ex.exercise_name)
            we = WorkoutExercise(
                workout_id=workout.id,
                exercise_id=gen_uuid(),
                exercise_name=ex.exercise_name,
                order=order,
            )
            self.db.add(we)
            await self.db.flush()
            for s_order, s in enumerate(sorted(ex.sets, key=lambda x: x.order)):
                weight = round(max_kg * s.percent_1rm / 100 / 2.5) * 2.5 if max_kg else 0.0
                self.db.add(ExerciseSet(
                    workout_exercise_id=we.id,
                    weight=weight,
                    reps=s.reps,
                    completed=False,
                    order=s_order,
                ))

        existing_log = next((l for l in run.logs if l.cycle_workout_id == cycle_workout.id), None)
        if existing_log:
            existing_log.workout_id = workout.id
            log = existing_log
        else:
            log = CycleWorkoutLog(run_id=run.id, cycle_workout_id=cycle_workout.id, workout_id=workout.id)
            self.db.add(log)

        await self.db.commit()
        return workout, log

    async def complete_workout_log(
        self,
        run: UserCycleRun,
        cycle_workout_id: str,
        workout_id: str | None,
    ) -> UserCycleRun:
        log = next((l for l in run.logs if l.cycle_workout_id == cycle_workout_id), None)
        if log:
            if workout_id:
                log.workout_id = workout_id
        else:
            log = CycleWorkoutLog(run_id=run.id, cycle_workout_id=cycle_workout_id, workout_id=workout_id)
            self.db.add(log)
        log.completed_at = datetime.utcnow()
        await self.db.commit()
        return await self.get_run_by_id(run.id, run.user_id)  # type: ignore[return-value]

    async def finish_run(self, run: UserCycleRun) -> UserCycleRun:
        run.completed_at = datetime.utcnow()
        await self.db.commit()
        return await self.get_run_by_id(run.id, run.user_id)  # type: ignore[return-value]

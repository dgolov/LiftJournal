from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import CycleRunOut, CycleWorkoutLogOut
from app.repositories.cycle_run import CycleRunRepository
from app.domain.models import UserCycleRun


class CycleRunService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = CycleRunRepository(db)

    def _to_dto(self, run: UserCycleRun) -> CycleRunOut:
        return CycleRunOut(
            id=run.id,
            cycle_id=run.cycle_id,
            started_at=run.started_at,
            completed_at=run.completed_at,
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

    async def get_active_run(self, cycle_id: str, user_id: int) -> CycleRunOut | None:
        run = await self.repo.get_active_run(user_id, cycle_id)
        return self._to_dto(run) if run else None

    async def start_run(self, cycle_id: str, user_id: int) -> CycleRunOut:
        run = await self.repo.get_active_run(user_id, cycle_id)
        if run:
            return self._to_dto(run)
        cycle = await self.repo.get_cycle(cycle_id)
        if not cycle:
            raise HTTPException(status_code=404, detail="Цикл не найден")
        if not cycle.is_public and cycle.created_by != user_id:
            raise HTTPException(status_code=403, detail="Нет доступа")
        run = await self.repo.create_run(user_id, cycle_id)
        return self._to_dto(run)

    async def start_workout(
        self, run_id: str, cycle_workout_id: str, notes: str, user_id: int
    ) -> dict:
        run = await self.repo.get_run_by_id(run_id, user_id)
        if not run:
            raise HTTPException(status_code=404, detail="Прогон цикла не найден")
        existing_log = next((l for l in run.logs if l.cycle_workout_id == cycle_workout_id), None)
        if existing_log and existing_log.workout_id:
            return {"run_id": run.id, "log_id": existing_log.id, "workout_id": existing_log.workout_id}
        cycle_workout = await self.repo.get_cycle_workout(cycle_workout_id)
        if not cycle_workout or cycle_workout.cycle_id != run.cycle_id:
            raise HTTPException(status_code=404, detail="Тренировка цикла не найдена")
        cycle = await self.repo.get_cycle(run.cycle_id)
        maxes = await self.repo.get_user_maxes(user_id)
        workout, log = await self.repo.create_prefilled_workout(
            run, cycle_workout, cycle.title, notes, maxes  # type: ignore[union-attr]
        )
        return {"run_id": run.id, "log_id": log.id, "workout_id": workout.id}

    async def complete_workout(
        self, run_id: str, cycle_workout_id: str, workout_id: str | None, user_id: int
    ) -> CycleRunOut:
        run = await self.repo.get_run_by_id(run_id, user_id)
        if not run:
            raise HTTPException(status_code=404, detail="Прогон цикла не найден")
        run = await self.repo.complete_workout_log(run, cycle_workout_id, workout_id)
        return self._to_dto(run)

    async def finish_run(self, run_id: str, user_id: int) -> CycleRunOut:
        run = await self.repo.get_run_by_id(run_id, user_id)
        if not run:
            raise HTTPException(status_code=404, detail="Прогон цикла не найден")
        run = await self.repo.finish_run(run)
        return self._to_dto(run)

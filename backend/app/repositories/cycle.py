from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import TrainingCycle, CycleWorkout, CycleExercise, CycleSet


class CycleRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _eager(self):
        return (
            selectinload(TrainingCycle.workouts)
            .selectinload(CycleWorkout.exercises)
            .selectinload(CycleExercise.sets)
        )

    async def get_all_visible(self, user_id: int) -> tuple[list[TrainingCycle], dict[str, int]]:
        result = await self.db.execute(
            select(TrainingCycle)
            .where(
                (TrainingCycle.is_public == True) | (TrainingCycle.created_by == user_id)  # noqa: E712
            )
            .order_by(TrainingCycle.created_at.desc())
        )
        cycles = list(result.scalars().all())

        count_result = await self.db.execute(
            select(CycleWorkout.cycle_id, func.count(CycleWorkout.id).label("cnt"))
            .group_by(CycleWorkout.cycle_id)
        )
        counts = {row.cycle_id: row.cnt for row in count_result}
        return cycles, counts

    async def get_by_id(self, cycle_id: str) -> TrainingCycle | None:
        result = await self.db.execute(
            select(TrainingCycle).options(self._eager()).where(TrainingCycle.id == cycle_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        created_by: int,
        title: str,
        description: str,
        author_name: str,
        is_public: bool,
        workouts_data,
    ) -> TrainingCycle:
        cycle = TrainingCycle(
            created_by=created_by,
            title=title,
            description=description,
            author_name=author_name,
            is_public=is_public,
            created_at=datetime.utcnow(),
        )
        cycle.workouts = self._build_workouts(workouts_data)
        self.db.add(cycle)
        await self.db.commit()
        return await self.get_by_id(cycle.id)  # type: ignore[return-value]

    async def update(
        self,
        cycle: TrainingCycle,
        *,
        title: str | None = None,
        description: str | None = None,
        author_name: str | None = None,
        is_public: bool | None = None,
        workouts_data=None,
    ) -> TrainingCycle:
        if title is not None:
            cycle.title = title
        if description is not None:
            cycle.description = description
        if author_name is not None:
            cycle.author_name = author_name
        if is_public is not None:
            cycle.is_public = is_public
        if workouts_data is not None:
            cycle.workouts = self._build_workouts(workouts_data)
        await self.db.commit()
        return await self.get_by_id(cycle.id)  # type: ignore[return-value]

    async def delete(self, cycle: TrainingCycle) -> None:
        await self.db.delete(cycle)
        await self.db.commit()

    def _build_workouts(self, workouts_in) -> list[CycleWorkout]:
        result = []
        for i, w_in in enumerate(workouts_in or []):
            w = CycleWorkout(
                workout_number=w_in.workout_number,
                title=w_in.title,
                notes=w_in.notes,
                order=i,
            )
            for j, e_in in enumerate(w_in.exercises):
                e = CycleExercise(
                    exercise_id=e_in.exercise_id,
                    exercise_name=e_in.exercise_name,
                    order=j,
                )
                e.sets = [
                    CycleSet(percent_1rm=s.percent_1rm, reps=s.reps, order=k)
                    for k, s in enumerate(e_in.sets)
                ]
                w.exercises.append(e)
            result.append(w)
        return result

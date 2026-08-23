from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import ExerciseCreate, ExerciseOut
from app.repositories.exercise import ExerciseRepository


class ExerciseService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = ExerciseRepository(db)

    def _to_dto(self, e) -> ExerciseOut:
        return ExerciseOut(
            id=e.id,
            name=e.name,
            muscleGroup=e.muscle_group,
            secondaryMuscles=e.secondary_muscles or [],
            equipment=e.equipment,
            description=e.description or "",
            isCustom=e.is_custom,
            status=e.status,
        )

    async def list_exercises(self, user_id: int) -> list[ExerciseOut]:
        return [self._to_dto(e) for e in await self.repo.get_all(user_id)]

    async def create_custom(self, data: ExerciseCreate, user_id: int) -> ExerciseOut:
        e = await self.repo.create(
            name=data.name,
            muscle_group=data.muscleGroup,
            secondary_muscles=data.secondaryMuscles,
            equipment=data.equipment,
            description=data.description,
            created_by=user_id,
            is_private=data.isPrivate,
        )
        return self._to_dto(e)

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import AdminUserOut, AdminExerciseOut
from app.domain.models import Exercise
from app.repositories.admin import AdminRepository


class AdminService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = AdminRepository(db)

    def _exercise_to_dto(self, e: Exercise, submitter=None) -> AdminExerciseOut:
        return AdminExerciseOut(
            id=e.id,
            name=e.name,
            muscleGroup=e.muscle_group,
            secondaryMuscles=e.secondary_muscles or [],
            equipment=e.equipment,
            description=e.description or "",
            isApproved=e.is_approved,
            submittedByName=submitter.name if submitter else None,
            submittedByEmail=submitter.email if submitter else None,
        )

    async def list_users(self) -> list[AdminUserOut]:
        return [
            AdminUserOut(id=u.id, email=u.email, name=u.name, isAdmin=u.is_admin)
            for u in await self.repo.get_all_users()
        ]

    async def list_pending_exercises(self) -> list[AdminExerciseOut]:
        rows = await self.repo.get_pending_exercises()
        return [self._exercise_to_dto(ex, submitter) for ex, submitter in rows]

    async def approve_exercise(self, exercise_id: str) -> AdminExerciseOut:
        ex = await self.repo.get_exercise_by_id(exercise_id)
        if not ex:
            raise HTTPException(status_code=404, detail="Exercise not found")
        ex = await self.repo.approve_exercise(ex)
        return self._exercise_to_dto(ex)

    async def reject_exercise(self, exercise_id: str) -> None:
        ex = await self.repo.get_exercise_by_id(exercise_id)
        if not ex:
            raise HTTPException(status_code=404, detail="Exercise not found")
        await self.repo.delete_exercise(ex)

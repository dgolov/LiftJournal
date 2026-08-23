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
            isPrivate=e.is_private,
            submittedByName=submitter.name if submitter else None,
            submittedByEmail=submitter.email if submitter else None,
        )

    async def list_users(self) -> list[AdminUserOut]:
        return [
            AdminUserOut(id=u.id, email=u.email, name=u.name, isAdmin=u.is_admin)
            for u in await self.repo.get_all_users()
        ]

    async def list_exercises(self, status: str = "pending") -> list[AdminExerciseOut]:
        rows = await self.repo.get_exercises(pending_only=(status != "all"))
        return [self._exercise_to_dto(ex, submitter) for ex, submitter in rows]

    async def approve_exercise(self, exercise_id: str) -> AdminExerciseOut:
        ex = await self._get_exercise_or_404(exercise_id)
        ex = await self.repo.approve_exercise(ex)
        return self._exercise_to_dto(ex)

    async def revoke_exercise(self, exercise_id: str) -> AdminExerciseOut:
        """Take an approved+public exercise back to creator-only visibility.
        Unlike reject, this never deletes the row — workout history may still
        reference it."""
        ex = await self._get_exercise_or_404(exercise_id)
        ex = await self.repo.revoke_exercise(ex)
        return self._exercise_to_dto(ex)

    async def rename_exercise(self, exercise_id: str, name: str) -> AdminExerciseOut:
        ex = await self._get_exercise_or_404(exercise_id)
        ex = await self.repo.rename_exercise(ex, name)
        return self._exercise_to_dto(ex)

    async def reject_exercise(self, exercise_id: str) -> None:
        ex = await self._get_exercise_or_404(exercise_id)
        if ex.is_approved and not ex.is_private:
            raise HTTPException(
                status_code=400,
                detail="Нельзя удалить опубликованное упражнение — используйте отзыв доступа",
            )
        await self.repo.delete_exercise(ex)

    async def _get_exercise_or_404(self, exercise_id: str) -> Exercise:
        ex = await self.repo.get_exercise_by_id(exercise_id)
        if not ex:
            raise HTTPException(status_code=404, detail="Exercise not found")
        return ex

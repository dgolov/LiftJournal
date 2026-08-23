from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    AdminUserOut, AdminExerciseOut, AdminCycleOut, AdminStatsOut, DailyCountOut, TopUserOut,
)
from app.domain.models import Exercise, TrainingCycle, User
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
            status=e.status,
            submittedByName=submitter.name if submitter else None,
            submittedByEmail=submitter.email if submitter else None,
        )

    async def list_users(self) -> list[AdminUserOut]:
        return [
            AdminUserOut(id=u.id, email=u.email, name=u.name, isAdmin=u.is_admin)
            for u in await self.repo.get_all_users()
        ]

    async def set_user_admin(self, user_id: int, is_admin: bool, current_admin_id: int) -> AdminUserOut:
        if user_id == current_admin_id and not is_admin:
            raise HTTPException(
                status_code=400,
                detail="Нельзя снять права администратора с самого себя",
            )
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user = await self.repo.set_user_admin(user, is_admin)
        return AdminUserOut(id=user.id, email=user.email, name=user.name, isAdmin=user.is_admin)

    async def list_exercises(
        self, status: str = "pending", search: str | None = None, muscle_group: str | None = None
    ) -> list[AdminExerciseOut]:
        rows = await self.repo.get_exercises(status=status, search=search, muscle_group=muscle_group)
        return [self._exercise_to_dto(ex, submitter) for ex, submitter in rows]

    async def approve_exercise(self, exercise_id: str) -> AdminExerciseOut:
        """Allowed from pending (normal moderation) or rejected (admin
        reconsiders) — approving is always a forward move, never blocked."""
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
        """Marks a pending submission as rejected — it stays in the database
        (visible in the admin's "all" list and to its creator) rather than
        being deleted, so a rejection is never just silently invisible."""
        ex = await self._get_exercise_or_404(exercise_id)
        if ex.status != "pending":
            raise HTTPException(
                status_code=400,
                detail="Можно отклонить только упражнение на модерации",
            )
        await self.repo.reject_exercise(ex)

    async def _get_exercise_or_404(self, exercise_id: str) -> Exercise:
        ex = await self.repo.get_exercise_by_id(exercise_id)
        if not ex:
            raise HTTPException(status_code=404, detail="Exercise not found")
        return ex

    def _cycle_to_dto(self, c: TrainingCycle, submitter=None, workout_count: int = 0) -> AdminCycleOut:
        return AdminCycleOut(
            id=c.id,
            title=c.title,
            description=c.description or "",
            authorName=c.author_name or "",
            isPublic=c.is_public,
            isApproved=c.is_approved,
            workoutCount=workout_count,
            createdAt=c.created_at,
            submittedByName=submitter.name if submitter else None,
            submittedByEmail=submitter.email if submitter else None,
        )

    async def list_cycles(self, status: str = "pending") -> list[AdminCycleOut]:
        rows, counts = await self.repo.get_cycles(pending_only=(status != "all"))
        return [self._cycle_to_dto(c, submitter, counts.get(c.id, 0)) for c, submitter in rows]

    async def approve_cycle(self, cycle_id: str) -> AdminCycleOut:
        c = await self._get_cycle_or_404(cycle_id)
        c = await self.repo.approve_cycle(c)
        return self._cycle_to_dto(c)

    async def revoke_cycle(self, cycle_id: str) -> AdminCycleOut:
        """Take a public+approved cycle back to creator-only. Unlike reject,
        this never deletes the row — UserCycleRun cascades on cycle delete,
        so removing a cycle with real runs would wipe that history."""
        c = await self._get_cycle_or_404(cycle_id)
        c = await self.repo.revoke_cycle(c)
        return self._cycle_to_dto(c)

    async def reject_cycle(self, cycle_id: str) -> None:
        c = await self._get_cycle_or_404(cycle_id)
        if c.is_public and c.is_approved:
            raise HTTPException(
                status_code=400,
                detail="Нельзя удалить опубликованный цикл — используйте отзыв доступа",
            )
        await self.repo.delete_cycle(c)

    async def _get_cycle_or_404(self, cycle_id: str) -> TrainingCycle:
        c = await self.repo.get_cycle_by_id(cycle_id)
        if not c:
            raise HTTPException(status_code=404, detail="Cycle not found")
        return c

    async def get_stats(self) -> AdminStatsOut:
        data = await self.repo.get_stats_data()

        counts_by_date = {d.isoformat() if hasattr(d, "isoformat") else str(d): c for d, c in data["daily_rows"]}
        today = datetime.utcnow().date()
        daily = [
            DailyCountOut(date=(today - timedelta(days=i)).isoformat(), count=counts_by_date.get((today - timedelta(days=i)).isoformat(), 0))
            for i in range(13, -1, -1)
        ]

        top_users = [TopUserOut(id=uid, name=name, workoutCount=cnt) for uid, cnt, name in data["top_rows"]]

        return AdminStatsOut(
            totalUsers=data["total_users"],
            newUsersLast7Days=data["new_users_7d"],
            totalWorkouts=data["total_workouts"],
            workoutsLast7Days=data["workouts_7d"],
            totalExercises=data["total_exercises"],
            customExercises=data["custom_exercises"],
            pendingExercises=data["pending_exercises"],
            totalCycles=data["total_cycles"],
            publicCycles=data["public_cycles"],
            pendingCycles=data["pending_cycles"],
            dailyWorkouts=daily,
            topUsers=top_users,
        )

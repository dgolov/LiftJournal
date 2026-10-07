from datetime import date, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    CoachLinkOut, CoachLinkPermissionsUpdate, AthleteSummaryOut,
    PlannedWorkoutCreate, PlannedWorkoutUpdate, PlannedWorkoutOut,
    WorkoutOut, UserMaxOut, WeightEntryOut,
)
from app.domain.models import CoachAthlete, User
from app.repositories.coach import CoachRepository
from app.repositories.planned_workout import PlannedWorkoutRepository
from app.repositories.social import SocialRepository
from app.services.notifications import NotificationService
from app.services.planned_workout import PlannedWorkoutService
from app.services.workout import WorkoutService

# Without an active link the athlete's coach-only data must look nonexistent:
# a 403 would confirm to anyone probing ids that a relationship exists.
NOT_FOUND = HTTPException(status_code=404, detail="Подопечный не найден")


class CoachService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = CoachRepository(db)

    # ── DTO ──────────────────────────────────────────────────────────────────

    @staticmethod
    def _link_to_dto(link: CoachAthlete, coach: User, athlete: User) -> CoachLinkOut:
        return CoachLinkOut(
            id=link.id,
            coachId=coach.id,
            coachName=coach.name,
            coachAvatarUrl=coach.avatar_url,
            athleteId=athlete.id,
            athleteName=athlete.name,
            athleteAvatarUrl=athlete.avatar_url,
            status=link.status,
            initiatedBy=link.initiated_by,
            canSeePrivate=link.can_see_private,
            canEditPlan=link.can_edit_plan,
            message=link.message or "",
            createdAt=link.created_at,
            respondedAt=link.responded_at,
            endedAt=link.ended_at,
        )

    async def _link_dto(self, link: CoachAthlete) -> CoachLinkOut:
        coach = await self.repo.get_user(link.coach_id)
        athlete = await self.repo.get_user(link.athlete_id)
        return self._link_to_dto(link, coach, athlete)

    # ── Creating links ───────────────────────────────────────────────────────

    async def invite(self, coach_id: int, athlete_id: int, message: str) -> CoachLinkOut:
        if coach_id == athlete_id:
            raise HTTPException(status_code=400, detail="Нельзя пригласить самого себя")
        coach = await self.repo.get_user(coach_id)
        if not coach or not coach.is_coach:
            raise HTTPException(status_code=403, detail="Сначала включите роль тренера в профиле")
        athlete = await self.repo.get_user(athlete_id)
        if not athlete:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        if not await self.repo.is_following(athlete_id, coach_id):
            raise HTTPException(status_code=400, detail="Пригласить можно только своего подписчика")
        if await self.repo.get_open_link(coach_id, athlete_id):
            raise HTTPException(status_code=409, detail="Приглашение уже отправлено или пользователь уже ваш подопечный")

        link = await self.repo.create_link(
            coach_id=coach_id, athlete_id=athlete_id, initiated_by="coach", message=message.strip(),
        )
        await NotificationService(self.db).notify_coach_invite(coach_id, athlete_id, link.id, link.message)
        return self._link_to_dto(link, coach, athlete)

    async def request(self, athlete_id: int, coach_id: int, message: str) -> CoachLinkOut:
        if coach_id == athlete_id:
            raise HTTPException(status_code=400, detail="Нельзя стать подопечным самого себя")
        coach = await self.repo.get_user(coach_id)
        if not coach or not coach.is_coach:
            raise HTTPException(status_code=404, detail="Тренер не найден")
        if not coach.coach_accepting:
            raise HTTPException(status_code=400, detail="Тренер сейчас не набирает подопечных")
        if await self.repo.get_open_link(coach_id, athlete_id):
            raise HTTPException(status_code=409, detail="Заявка уже отправлена или вы уже занимаетесь у этого тренера")
        athlete = await self.repo.get_user(athlete_id)

        link = await self.repo.create_link(
            coach_id=coach_id, athlete_id=athlete_id, initiated_by="athlete", message=message.strip(),
        )
        await NotificationService(self.db).notify_coach_request(athlete_id, coach_id, link.id, link.message)
        return self._link_to_dto(link, coach, athlete)

    # ── Responding / ending ──────────────────────────────────────────────────

    async def _get_own_link(self, link_id: str, user_id: int) -> CoachAthlete:
        link = await self.repo.get_link(link_id)
        if not link or user_id not in (link.coach_id, link.athlete_id):
            raise HTTPException(status_code=404, detail="Связь не найдена")
        return link

    @staticmethod
    def _initiator_id(link: CoachAthlete) -> int:
        return link.coach_id if link.initiated_by == "coach" else link.athlete_id

    async def _respond(self, link_id: str, user_id: int, accept: bool) -> CoachLinkOut:
        link = await self._get_own_link(link_id, user_id)
        if link.status != "pending":
            raise HTTPException(status_code=409, detail="Заявка уже обработана")
        if self._initiator_id(link) == user_id:
            raise HTTPException(status_code=403, detail="Ответить может только вторая сторона")
        link.status = "active" if accept else "declined"
        link.responded_at = datetime.utcnow()
        link = await self.repo.save(link)
        if accept:
            await NotificationService(self.db).notify_coach_accepted(user_id, self._initiator_id(link), link.id)
        return await self._link_dto(link)

    async def accept(self, link_id: str, user_id: int) -> CoachLinkOut:
        return await self._respond(link_id, user_id, accept=True)

    async def decline(self, link_id: str, user_id: int) -> CoachLinkOut:
        return await self._respond(link_id, user_id, accept=False)

    async def cancel(self, link_id: str, user_id: int) -> None:
        """The initiator withdraws an unanswered invite/request."""
        link = await self._get_own_link(link_id, user_id)
        if link.status != "pending":
            raise HTTPException(status_code=409, detail="Отменить можно только неотвеченную заявку")
        if self._initiator_id(link) != user_id:
            raise HTTPException(status_code=403, detail="Отменить может только отправитель")
        await self.repo.delete(link)

    async def end(self, link_id: str, user_id: int) -> CoachLinkOut:
        """Either side ends an active relationship. Plans the coach wrote stay
        with the athlete — they're the athlete's data."""
        link = await self._get_own_link(link_id, user_id)
        if link.status != "active":
            raise HTTPException(status_code=409, detail="Сотрудничество не активно")
        link.status = "ended"
        link.ended_at = datetime.utcnow()
        link = await self.repo.save(link)
        return await self._link_dto(link)

    async def update_permissions(
        self, link_id: str, user_id: int, data: CoachLinkPermissionsUpdate,
    ) -> CoachLinkOut:
        link = await self._get_own_link(link_id, user_id)
        if link.athlete_id != user_id:
            raise HTTPException(status_code=403, detail="Права меняет только подопечный")
        if link.status not in ("pending", "active"):
            raise HTTPException(status_code=409, detail="Сотрудничество завершено")
        if data.canSeePrivate is not None:
            link.can_see_private = data.canSeePrivate
        if data.canEditPlan is not None:
            link.can_edit_plan = data.canEditPlan
        link = await self.repo.save(link)
        return await self._link_dto(link)

    async def list_links(
        self, user_id: int, role: str | None, statuses: list[str] | None,
    ) -> list[CoachLinkOut]:
        rows = await self.repo.list_links(user_id, role, statuses)
        return [self._link_to_dto(link, coach, athlete) for link, coach, athlete in rows]

    # ── Athletes ─────────────────────────────────────────────────────────────

    async def _summary(self, link: CoachAthlete, athlete: User) -> AthleteSummaryOut:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        return AthleteSummaryOut(
            linkId=link.id,
            id=athlete.id,
            name=athlete.name,
            avatarUrl=athlete.avatar_url,
            canSeePrivate=link.can_see_private,
            canEditPlan=link.can_edit_plan,
            since=link.responded_at,
            lastWorkoutDate=await self.repo.last_workout_date(athlete.id),
            weekPlanned=await self.repo.count_planned(athlete.id, week_start, week_end),
            weekCompleted=await self.repo.count_workouts(athlete.id, week_start, week_end),
        )

    async def get_athletes(self, coach_id: int) -> list[AthleteSummaryOut]:
        rows = await self.repo.list_links(coach_id, "coach", ["active"])
        result = [await self._summary(link, athlete) for link, _coach, athlete in rows]
        return sorted(result, key=lambda a: a.name.lower())

    async def _require_link(
        self, coach_id: int, athlete_id: int, *, private: bool = False, edit_plan: bool = False,
    ) -> CoachAthlete:
        link = await self.repo.get_active_link(coach_id, athlete_id)
        if not link:
            raise NOT_FOUND
        if private and not link.can_see_private:
            raise HTTPException(status_code=403, detail="Подопечный скрыл эти данные")
        if edit_plan and not link.can_edit_plan:
            raise HTTPException(status_code=403, detail="Подопечный запретил менять свой план")
        return link

    async def get_athlete(self, coach_id: int, athlete_id: int) -> AthleteSummaryOut:
        link = await self._require_link(coach_id, athlete_id)
        athlete = await self.repo.get_user(athlete_id)
        if not athlete:
            raise NOT_FOUND
        return await self._summary(link, athlete)

    async def get_athlete_workouts(
        self, coach_id: int, athlete_id: int, date_from: date | None, date_to: date | None,
    ) -> list[WorkoutOut]:
        await self._require_link(coach_id, athlete_id)
        return await WorkoutService(self.db).get_workouts(athlete_id, date_from=date_from, date_to=date_to)

    async def get_athlete_planned(
        self, coach_id: int, athlete_id: int, date_from: date | None, date_to: date | None,
    ) -> list[PlannedWorkoutOut]:
        await self._require_link(coach_id, athlete_id)
        plans = await PlannedWorkoutRepository(self.db).get_by_user_range(
            athlete_id, date_from=date_from, date_to=date_to,
        )
        svc = PlannedWorkoutService(self.db)
        return [svc._to_dto(p) for p in plans]

    async def get_athlete_maxes(self, coach_id: int, athlete_id: int) -> list[UserMaxOut]:
        await self._require_link(coach_id, athlete_id, private=True)
        maxes = await SocialRepository(self.db).get_user_maxes(athlete_id)
        return [
            UserMaxOut(exercise_name=m.exercise_name, weight_kg=m.weight_kg, recorded_at=m.recorded_at)
            for m in maxes
        ]

    async def get_athlete_weight(self, coach_id: int, athlete_id: int) -> list[WeightEntryOut]:
        await self._require_link(coach_id, athlete_id, private=True)
        return [WeightEntryOut(date=e.date, kg=e.kg) for e in await self.repo.get_weight_log(athlete_id)]

    # ── Planning for an athlete ──────────────────────────────────────────────

    async def create_plan(
        self, coach_id: int, athlete_id: int, data: PlannedWorkoutCreate,
    ) -> PlannedWorkoutOut:
        await self._require_link(coach_id, athlete_id, edit_plan=True)
        await PlannedWorkoutService(self.db).check_cycle(data.cycleId, coach_id)
        repo = PlannedWorkoutRepository(self.db)
        plan = await repo.create(
            user_id=athlete_id,
            created_by=coach_id,
            cycle_id=data.cycleId,
            cycle_schedule_id=data.cycleScheduleId,
            title=data.title,
            type=data.type,
            scheduled_date=data.scheduledDate,
            notes=data.notes,
            exercises_data=data.exercises,
        )
        await NotificationService(self.db).notify_plan_assigned(coach_id, athlete_id, plan.id, plan.title)
        return PlannedWorkoutService(self.db)._to_dto(plan)

    async def _get_editable_plan(self, coach_id: int, athlete_id: int, plan_id: str):
        await self._require_link(coach_id, athlete_id, edit_plan=True)
        repo = PlannedWorkoutRepository(self.db)
        plan = await repo.get_by_id(plan_id)
        if not plan or plan.user_id != athlete_id:
            raise HTTPException(status_code=404, detail="План не найден")
        if plan.status != "planned":
            raise HTTPException(status_code=409, detail="Выполненный или пропущенный план менять нельзя")
        return repo, plan

    async def update_plan(
        self, coach_id: int, athlete_id: int, plan_id: str, data: PlannedWorkoutUpdate,
    ) -> PlannedWorkoutOut:
        repo, plan = await self._get_editable_plan(coach_id, athlete_id, plan_id)
        # Completing or skipping is the athlete's call, not the coach's.
        plan = await repo.update(
            plan,
            title=data.title,
            type=data.type,
            scheduled_date=data.scheduledDate,
            notes=data.notes,
            exercises_data=data.exercises,
        )
        return PlannedWorkoutService(self.db)._to_dto(plan)

    async def delete_plan(self, coach_id: int, athlete_id: int, plan_id: str) -> None:
        repo, plan = await self._get_editable_plan(coach_id, athlete_id, plan_id)
        await repo.delete(plan)

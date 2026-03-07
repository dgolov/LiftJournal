from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.db.models import User, WeightEntry, Goal
from app.schemas import (
    ProfileUpdate, WeightEntryIn, WeightEntryOut,
    GoalCreate, GoalOut, UserOut,
)

router = APIRouter()

USER_ID = 1


def _user_with_relations():
    return (
        selectinload(User.weight_log),
        selectinload(User.goals),
    )


async def _get_user(db: AsyncSession) -> User:
    result = await db.execute(
        select(User)
        .options(*_user_with_relations())
        .where(User.id == USER_ID)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _serialize_user(u: User) -> UserOut:
    weight_log = sorted(u.weight_log, key=lambda e: e.date)
    return UserOut(
        name=u.name,
        age=u.age,
        avatarUrl=u.avatar_url,
        weightLog=[WeightEntryOut(date=e.date, kg=e.kg) for e in weight_log],
        goals=[
            GoalOut(id=g.id, text=g.text, targetDate=g.target_date, done=g.done)
            for g in u.goals
        ],
    )


@router.get("", response_model=UserOut)
async def get_user(db: AsyncSession = Depends(get_db)):
    return _serialize_user(await _get_user(db))


@router.patch("/profile", response_model=UserOut)
async def update_profile(payload: ProfileUpdate, db: AsyncSession = Depends(get_db)):
    u = await _get_user(db)
    if payload.name is not None:
        u.name = payload.name
    if payload.age is not None:
        u.age = payload.age
    if payload.avatarUrl is not None:
        u.avatar_url = payload.avatarUrl
    await db.commit()
    return _serialize_user(await _get_user(db))


@router.post("/weight", response_model=WeightEntryOut)
async def log_weight(payload: WeightEntryIn, db: AsyncSession = Depends(get_db)):
    # upsert by date — replace existing entry for that day
    result = await db.execute(
        select(WeightEntry).where(
            WeightEntry.user_id == USER_ID, WeightEntry.date == payload.date
        )
    )
    entry = result.scalar_one_or_none()
    if entry:
        entry.kg = payload.kg
    else:
        entry = WeightEntry(user_id=USER_ID, date=payload.date, kg=payload.kg)
        db.add(entry)
    await db.commit()
    return WeightEntryOut(date=entry.date, kg=entry.kg)


@router.delete("/weight/{entry_date}", status_code=204)
async def delete_weight(entry_date: str, db: AsyncSession = Depends(get_db)):
    from datetime import date as date_type
    try:
        d = date_type.fromisoformat(entry_date)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid date format")
    result = await db.execute(
        select(WeightEntry).where(WeightEntry.user_id == USER_ID, WeightEntry.date == d)
    )
    entry = result.scalar_one_or_none()
    if entry:
        await db.delete(entry)
        await db.commit()


@router.post("/goals", response_model=GoalOut, status_code=201)
async def create_goal(payload: GoalCreate, db: AsyncSession = Depends(get_db)):
    goal = Goal(
        user_id=USER_ID,
        text=payload.text,
        target_date=payload.targetDate,
        done=payload.done,
    )
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    return GoalOut(id=goal.id, text=goal.text, targetDate=goal.target_date, done=goal.done)


@router.patch("/goals/{goal_id}/toggle", response_model=GoalOut)
async def toggle_goal(goal_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == USER_ID)
    )
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    goal.done = not goal.done
    await db.commit()
    return GoalOut(id=goal.id, text=goal.text, targetDate=goal.target_date, done=goal.done)


@router.delete("/goals/{goal_id}", status_code=204)
async def delete_goal(goal_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Goal).where(Goal.id == goal_id, Goal.user_id == USER_ID)
    )
    goal = result.scalar_one_or_none()
    if goal:
        await db.delete(goal)
        await db.commit()

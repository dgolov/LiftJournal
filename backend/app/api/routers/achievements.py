from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import AchievementOut
from app.core.database import get_db
from app.core.security import get_current_user
from app.domain.models import User
from app.services.achievements import AchievementService

router = APIRouter()


@router.get("", response_model=list[AchievementOut])
async def list_achievements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await AchievementService(db).get_all(current_user.id)


@router.post("/evaluate", response_model=list[AchievementOut])
async def evaluate_achievements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Re-evaluate and unlock any newly earned achievements. Returns newly unlocked ones."""
    return await AchievementService(db).evaluate(current_user.id)

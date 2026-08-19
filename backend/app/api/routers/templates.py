from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import WorkoutTemplateCreate, WorkoutTemplateUpdate, WorkoutTemplateOut
from app.core.database import get_db
from app.core.security import get_current_user
from app.domain.models import User
from app.services.template import TemplateService

router = APIRouter()


@router.get("", response_model=list[WorkoutTemplateOut])
async def list_templates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await TemplateService(db).get_all(current_user.id)


@router.post("", response_model=WorkoutTemplateOut, status_code=201)
async def create_template(
    payload: WorkoutTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await TemplateService(db).create(payload, current_user.id)


@router.patch("/{template_id}", response_model=WorkoutTemplateOut)
async def update_template(
    template_id: str,
    payload: WorkoutTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await TemplateService(db).update(template_id, payload, current_user.id)


@router.delete("/{template_id}", status_code=204)
async def delete_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await TemplateService(db).delete(template_id, current_user.id)

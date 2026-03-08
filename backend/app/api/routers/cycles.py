from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import CycleCreate, CycleUpdate, CycleListOut, CycleDetailOut
from app.core.database import get_db
from app.core.security import get_current_user
from app.domain.models import User
from app.services.cycle import CycleService

router = APIRouter()


@router.get("", response_model=list[CycleListOut])
async def list_cycles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CycleService(db).list_cycles(current_user.id)


@router.post("", response_model=CycleDetailOut, status_code=201)
async def create_cycle(
    payload: CycleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CycleService(db).create_cycle(payload, current_user.id)


@router.get("/{cycle_id}", response_model=CycleDetailOut)
async def get_cycle(
    cycle_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CycleService(db).get_cycle(cycle_id, current_user.id)


@router.patch("/{cycle_id}", response_model=CycleDetailOut)
async def update_cycle(
    cycle_id: str,
    payload: CycleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await CycleService(db).update_cycle(cycle_id, payload, current_user.id)


@router.delete("/{cycle_id}", status_code=204)
async def delete_cycle(
    cycle_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await CycleService(db).delete_cycle(cycle_id, current_user.id)

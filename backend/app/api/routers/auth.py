from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import AuthRegister, AuthLogin, TokenOut
from app.core.database import get_db
from app.services.auth import AuthService


router = APIRouter()


@router.post("/register", response_model=TokenOut, status_code=201)
async def register(payload: AuthRegister, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).register(payload.email, payload.password, payload.name)


@router.post("/login", response_model=TokenOut)
async def login(payload: AuthLogin, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).login(payload.email, payload.password)

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import TokenOut
from app.core.security import hash_password, verify_password, create_access_token
from app.repositories.user import UserRepository


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)

    async def register(self, email: str, password: str, name: str) -> TokenOut:
        if await self.repo.get_by_email(email.lower()):
            raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
        user = await self.repo.create(
            email=email.lower(),
            hashed_password=hash_password(password),
            name=name,
        )
        return TokenOut(
            access_token=create_access_token(user.id),
            user_id=user.id,
            name=user.name,
        )

    async def login(self, email: str, password: str) -> TokenOut:
        user = await self.repo.get_by_email(email.lower())
        if not user or not user.hashed_password or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Неверный email или пароль")
        return TokenOut(
            access_token=create_access_token(user.id),
            user_id=user.id,
            name=user.name,
        )

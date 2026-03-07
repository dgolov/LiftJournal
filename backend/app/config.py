from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://gym:gym@localhost:5432/gym"
    secret_key: str = "change-me-in-production-please-use-long-random-string"
    access_token_expire_minutes: int = 60 * 24 * 30  # 30 days

    class Config:
        env_file = ".env"


settings = Settings()

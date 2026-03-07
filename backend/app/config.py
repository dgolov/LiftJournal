from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://gym:gym@localhost:5432/gym"

    class Config:
        env_file = ".env"


settings = Settings()

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./risk_assessment.db"
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    LOG_LEVEL: str = "INFO"
    VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

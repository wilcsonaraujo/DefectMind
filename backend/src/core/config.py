from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str
    APP_NAME: str
    APP_VERSION: str
    DATABASE_URL: Optional[str] = None

    # JWT
    JWT_SECRET_KEY: str = "changeme-insecure-default"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

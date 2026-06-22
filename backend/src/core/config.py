import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str
    APP_NAME: str
    APP_VERSION: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

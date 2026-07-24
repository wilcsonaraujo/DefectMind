from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str
    APP_NAME: str
    APP_VERSION: str
    DATABASE_URL: str | None = None

    # JWT
    JWT_SECRET_KEY: str = "changeme-insecure-default"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # NEO4J
    NEO4J_URI: str | None = None
    NEO4J_USER: str | None = None
    NEO4J_PASSWORD: str | None = None

    # GEMINI
    GEMINI_API_KEY: str | None = None

    # DEEPSEEK
    DEEPSEEK_API_KEY: str | None = None

    # GROQ
    GROQ_API_KEY: str | None = None

    # AI PROVIDER SELECTOR
    AI_PROVIDER: str = "groq"   # Valid values: "deepseek", "gemini", "groq"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

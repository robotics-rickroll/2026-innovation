from __future__ import annotations
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "artifact-classification"
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "changeme"
    access_token_expire_minutes: int = 60
    ai_provider: str = "mock"
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-3-flash-preview"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174"
    upload_dir: str = "./uploads"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

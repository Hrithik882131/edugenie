from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EduGenie"

    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"

    # Explanation
    explanation_provider: str = "gemini"
    local_explanation_model: str = "MBZUAI/LaMini-Flan-T5-783M"

    # Safety / free-tier protection
    max_input_chars: int = 12000
    max_output_tokens: int = 700

    # Minimum seconds between Gemini requests from this application.
    # This protects a free-tier key from rapid repeated clicks.
    request_cooldown_seconds: float = 3.0

    # Cache identical requests in memory.
    cache_enabled: bool = True
    cache_size: int = 100

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
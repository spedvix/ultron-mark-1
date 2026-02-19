from __future__ import annotations

import functools
import pathlib
from typing import List, Optional

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven configuration for the Ultron service."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ultron_env: str = Field("dev", alias="ULTRON_ENV")
    base_url: AnyHttpUrl = Field("https://ultron.local", alias="BASE_URL")
    timezone: str = Field("Europe/Istanbul", alias="TIMEZONE")
    database_url: str | None = Field(None, alias="DATABASE_URL")
    notion_api_key: Optional[str] = Field(None, alias="NOTION_API_KEY")
    notion_database_ids: List[str] = Field(default_factory=list, alias="NOTION_DATABASE_IDS")
    ann_base_urls: List[AnyHttpUrl] = Field(default_factory=list, alias="ANN_BASE_URLS")
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
    openai_chat_model: str = Field("gpt-5-mini", alias="OPENAI_CHAT_MODEL")

    imap_host: Optional[str] = Field(None, alias="IMAP_HOST")
    imap_email: Optional[str] = Field(None, alias="IMAP_EMAIL")
    imap_oauth_token: Optional[str] = Field(None, alias="IMAP_OAUTH_TOKEN")

    gmail_credentials_file: Optional[str] = Field(None, alias="GMAIL_CREDENTIALS_FILE")
    gmail_token_file: Optional[str] = Field(None, alias="GMAIL_TOKEN_FILE")

    google_calendar_token_file: Optional[str] = Field("data/google_calendar_token.json", alias="GOOGLE_CALENDAR_TOKEN_FILE")
    google_calendar_assignments_id: Optional[str] = Field("primary", alias="GOOGLE_CALENDAR_ASSIGNMENTS_ID")
    google_calendar_exams_id: Optional[str] = Field(None, alias="GOOGLE_CALENDAR_EXAMS_ID")
    google_calendar_schedule_id: Optional[str] = Field(None, alias="GOOGLE_CALENDAR_SCHEDULE_ID")
    google_calendar_timezone: str = Field("Europe/Istanbul", alias="GOOGLE_CALENDAR_TIMEZONE")

    log_level: str = Field("INFO", alias="LOG_LEVEL")
    mask_pii: bool = Field(True, alias="MASK_PII")

    scheduler_max_concurrency: int = Field(2, alias="SCHEDULER_MAX_CONCURRENCY")
    scheduler_timezone: Optional[str] = Field(None, alias="SCHEDULER_TIMEZONE")

    @property
    def is_dev(self) -> bool:
        return self.ultron_env.lower() == "dev"

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        if self.is_dev:
            db_path = pathlib.Path("data") / "ultron_dev.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite+aiosqlite:///{db_path}"
        raise ValueError("DATABASE_URL must be set in production mode")

    @property
    def scheduler_tz(self) -> str:
        return self.scheduler_timezone or self.timezone

    @field_validator("notion_database_ids", mode="before")
    @classmethod
    def split_comma_separated(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]

    @field_validator("ann_base_urls", mode="before")
    @classmethod
    def parse_ann_urls(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]


@functools.lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


settings = get_settings()

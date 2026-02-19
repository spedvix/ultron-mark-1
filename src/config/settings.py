"""
Configuration settings for Ultron
"""
from pathlib import Path

from loguru import logger as loguru_logger
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True
    )
    
    # University Website
    UNI_WEBSITE_URL: str = ""
    UNI_USERNAME: str = ""
    UNI_PASSWORD: str = ""
    ANNOUNCEMENTS_URL: str = ""
    ANNOUNCEMENT_ITEM_SELECTOR: str = "article.o_wblog_post"
    ANNOUNCEMENT_TITLE_SELECTOR: str = ".o_blog_post_title"
    ANNOUNCEMENT_DATE_SELECTOR: str = "time"
    ANNOUNCEMENT_CONTENT_SELECTOR: str = ".o_wblog_read_text"
    ANNOUNCEMENT_LINK_SELECTOR: str = ".o_blog_post_title"

    # Notion
    NOTION_API_KEY: str = ""
    NOTION_DATABASE_ID: str = ""  # Assignments/Tasks database
    NOTION_CALENDAR_ID: str = ""  # Schedule/Calendar database
    NOTION_COURSES_ID: str = ""   # Courses database (optional)

    # Google Calendar
    GOOGLE_CALENDAR_TOKEN_FILE: str = "data/google_calendar_token.json"
    GOOGLE_CALENDAR_ASSIGNMENTS_ID: str = ""
    GOOGLE_CALENDAR_EXAMS_ID: str = ""
    GOOGLE_CALENDAR_SCHEDULE_ID: str = ""
    GOOGLE_CALENDAR_TIMEZONE: str = "Europe/Istanbul"

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"  # Default model for chat
    
    # Anthropic (Optional)
    ANTHROPIC_API_KEY: str = ""
    
    # NightCrawler
    NIGHTCRAWLER_API_URL: str = "http://localhost:8000"
    NIGHTCRAWLER_API_KEY: str = ""
    
    # Dashboard
    DASHBOARD_HOST: str = "0.0.0.0"
    DASHBOARD_PORT: int = 8080
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/ultron.db"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE_NAME: str = "ultron.log"
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.DATA_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)


settings = Settings()

_LOG_SINK_CONFIGURED = False


def _configure_loguru_sink(log_path: Path, level: str) -> None:
    global _LOG_SINK_CONFIGURED
    if _LOG_SINK_CONFIGURED:
        return

    loguru_logger.add(
        log_path,
        rotation="24 hours",
        retention="7 days",
        encoding="utf-8",
        enqueue=True,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}",
        level=level.upper(),
    )
    _LOG_SINK_CONFIGURED = True


_configure_loguru_sink(settings.LOGS_DIR / settings.LOG_FILE_NAME, settings.LOG_LEVEL)

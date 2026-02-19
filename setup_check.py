"""
Quick start script for Ultron
Run this to check if everything is configured correctly
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from loguru import logger
from src.config.settings import settings
import os

logger.add("logs/setup_check.log", rotation="1 MB")


def check_env_vars():
    """Check if environment variables are set"""
    logger.info("Checking environment variables...")
    
    required_vars = [
        "UNI_WEBSITE_URL",
        "UNI_USERNAME",
        "UNI_PASSWORD",
        "NOTION_API_KEY",
        "NOTION_DATABASE_ID",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID",
        "OPENAI_API_KEY",
    ]
    
    missing = []
    for var in required_vars:
        value = getattr(settings, var, "")
        if not value or value == "":
            missing.append(var)
            logger.warning(f"❌ {var} is not set")
        else:
            logger.info(f"✅ {var} is set")
    
    if missing:
        logger.error(f"\n⚠️  Missing environment variables: {', '.join(missing)}")
        logger.error("Please configure these in your .env file")
        return False
    
    logger.info("✅ All required environment variables are set")
    return True


def check_dependencies():
    """Check if required packages are installed"""
    logger.info("\nChecking dependencies...")
    
    required_packages = [
        "selenium",
        "notion_client",
        "telegram",
        "openai",
        "fastapi",
        "uvicorn",
        "apscheduler",
        "sqlalchemy",
        "loguru"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} is installed")
        except ImportError:
            missing.append(package)
            logger.warning(f"❌ {package} is not installed")
    
    if missing:
        logger.error(f"\n⚠️  Missing packages: {', '.join(missing)}")
        logger.error("Run: pip install -r requirements.txt")
        return False
    
    logger.info("✅ All required packages are installed")
    return True


def check_directories():
    """Check if required directories exist"""
    logger.info("\nChecking directories...")
    
    dirs = [
        settings.DATA_DIR,
        settings.LOGS_DIR,
        Path(__file__).parent / "src" / "dashboard" / "templates",
        Path(__file__).parent / "src" / "dashboard" / "static"
    ]
    
    for dir_path in dirs:
        if dir_path.exists():
            logger.info(f"✅ {dir_path} exists")
        else:
            logger.warning(f"⚠️  {dir_path} does not exist, creating...")
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Created {dir_path}")
    
    return True


def test_notion_connection():
    """Test Notion API connection"""
    logger.info("\nTesting Notion connection...")
    
    try:
        from src.notion.notion_manager import NotionManager
        notion = NotionManager()
        
        # Try to get classes
        classes = notion.get_classes()
        logger.info(f"✅ Notion connection successful! Found {len(classes)} classes")
        return True
        
    except Exception as e:
        logger.error(f"❌ Notion connection failed: {e}")
        logger.error("Check your NOTION_API_KEY and NOTION_DATABASE_ID")
        return False


def test_openai_connection():
    """Test OpenAI API connection"""
    logger.info("\nTesting OpenAI connection...")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Try a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_completion_tokens=10
        )
        
        logger.info("✅ OpenAI connection successful!")
        return True
        
    except Exception as e:
        logger.error(f"❌ OpenAI connection failed: {e}")
        logger.error("Check your OPENAI_API_KEY")
        return False


def check_google_calendar():
    """Verify Google Calendar token and basic connectivity."""
    logger.info("
Checking Google Calendar configuration...")

    token_path = getattr(settings, 'google_calendar_token_file', None)
    if not token_path:
        logger.info("Google Calendar token not configured; skipping check.")
        return True

    path = Path(token_path)
    if not path.exists():
        logger.error(f"Google Calendar token file not found: {path}")
        logger.error("Run setup_google_calendar.py to generate the token or update GOOGLE_CALENDAR_TOKEN_FILE.")
        return False

    try:
        from src.google.calendar_manager import GoogleCalendarManager

        manager = GoogleCalendarManager()
        if not getattr(manager, 'client', None):
            logger.warning("Google Calendar client not initialised; check GOOGLE_CALENDAR_* settings.")
            return False

        manager.get_weekly_events()
        logger.info("Google Calendar connection successful!")
        return True
    except Exception as exc:
        logger.error(f"Google Calendar check failed: {exc}")
        return False

def initialize_database():
    """Initialize database"""
    logger.info("\nInitializing database...")
    
    try:
        from src.database.models import init_db
        init_db()
        logger.info("✅ Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False


def main():
    """Main setup check"""
    logger.info("=" * 60)
    logger.info("🤖 Ultron Setup Check")
    logger.info("=" * 60)
    
    # Check .env file exists
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        logger.error("\n❌ .env file not found!")
        logger.error("Copy .env.example to .env and fill in your credentials")
        logger.error("Run: Copy-Item .env.example .env")
        return
    
    checks = [
        ("Environment Variables", check_env_vars),
        ("Dependencies", check_dependencies),
        ("Directories", check_directories),
        ("Database", initialize_database),
        ("Notion Connection", test_notion_connection),
        ("OpenAI Connection", test_openai_connection),
        ("Google Calendar", check_google_calendar)
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            logger.error(f"Error during {name} check: {e}")
            results[name] = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Setup Check Summary")
    logger.info("=" * 60)
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    logger.info("=" * 60)
    
    if all_passed:
        logger.info("\n🎉 All checks passed! You're ready to run Ultron!")
        logger.info("\nRun: python main.py")
    else:
        logger.error("\n⚠️  Some checks failed. Please fix the issues above.")
        logger.error("\nSee SETUP.md for detailed instructions.")


if __name__ == "__main__":
    main()

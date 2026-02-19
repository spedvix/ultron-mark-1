"""
Setup script for Ultron AI Chat System
Installs all required dependencies and validates configuration
"""
import subprocess
import sys
from pathlib import Path
from loguru import logger


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        logger.error("Python 3.9 or higher is required")
        return False
    logger.success(f"Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def install_dependencies():
    """Install all required packages"""
    logger.info("Installing dependencies from requirements.txt...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"
        ])
        logger.success("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False


def check_env_file():
    """Check if .env file exists and has required keys"""
    env_path = Path(".env")
    
    if not env_path.exists():
        logger.warning(".env file not found!")
        logger.info("Creating .env template...")
        
        template = """# University Website
UNI_WEBSITE_URL=
UNI_USERNAME=
UNI_PASSWORD=

# Notion
NOTION_API_KEY=
NOTION_DATABASE_ID=
NOTION_CALENDAR_ID=

# Telegram
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=

# OpenAI (Required for Chat System)
OPENAI_API_KEY=

# Anthropic (Optional)
ANTHROPIC_API_KEY=

# NightCrawler
NIGHTCRAWLER_API_URL=http://localhost:8000
NIGHTCRAWLER_API_KEY=

# Dashboard
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8080

# Database
DATABASE_URL=sqlite:///./data/ultron.db

# Logging
LOG_LEVEL=INFO
"""
        
        env_path.write_text(template)
        logger.success(".env template created!")
        logger.warning("Please fill in your API keys in the .env file")
        return False
    
    # Check for required keys
    env_content = env_path.read_text()
    required_keys = ["OPENAI_API_KEY", "NOTION_API_KEY"]
    missing_keys = []
    
    for key in required_keys:
        if f"{key}=" in env_content and env_content.split(f"{key}=")[1].split("\n")[0].strip():
            logger.success(f"✓ {key} found")
        else:
            logger.warning(f"✗ {key} missing or empty")
            missing_keys.append(key)
    
    if missing_keys:
        logger.warning(f"Please add the following keys to your .env file: {', '.join(missing_keys)}")
        return False
    
    return True


def create_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "logs",
        "uploads"
    ]
    
    for dir_name in directories:
        path = Path(dir_name)
        if not path.exists():
            path.mkdir(parents=True)
            logger.info(f"Created directory: {dir_name}")
        else:
            logger.success(f"Directory exists: {dir_name}")
    
    return True


def test_imports():
    """Test if all critical imports work"""
    logger.info("Testing critical imports...")
    
    critical_imports = [
        ("openai", "OpenAI"),
        ("langchain", "LangChain"),
        ("langchain_openai", "LangChain OpenAI"),
        ("langgraph", "LangGraph"),
        ("fastapi", "FastAPI"),
        ("notion_client", "Notion Client"),
        ("PIL", "Pillow"),
        ("pypdf", "PyPDF"),
    ]
    
    failed_imports = []
    
    for module, name in critical_imports:
        try:
            __import__(module)
            logger.success(f"✓ {name}")
        except ImportError:
            logger.error(f"✗ {name} failed to import")
            failed_imports.append(name)
    
    if failed_imports:
        logger.error(f"Failed imports: {', '.join(failed_imports)}")
        logger.info("Try running: pip install -r requirements.txt")
        return False
    
    return True


def print_summary():
    """Print setup summary and next steps"""
    print("\n" + "="*60)
    print("🤖 ULTRON AI CHAT SYSTEM - SETUP COMPLETE")
    print("="*60)
    print("\n📋 NEXT STEPS:\n")
    print("1. Fill in your API keys in the .env file:")
    print("   - OPENAI_API_KEY (Required for AI chat)")
    print("   - NOTION_API_KEY (Required for academic data)")
    print("   - Other keys as needed")
    print()
    print("2. Start the dashboard:")
    print("   python main.py")
    print()
    print("3. Access the chat interface:")
    print("   http://localhost:8080/chat")
    print()
    print("📚 Documentation:")
    print("   - Chat System: CHAT_SYSTEM_DOCS.md")
    print("   - Development: DEVELOPMENT.md")
    print("   - Testing: TESTING_GUIDE.md")
    print()
    print("🔧 Troubleshooting:")
    print("   - Check logs in the console")
    print("   - Verify API keys are correct")
    print("   - Ensure Notion integration is set up")
    print()
    print("="*60)


def main():
    """Main setup function"""
    logger.info("Starting Ultron AI Chat System setup...\n")
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Installing dependencies", install_dependencies),
        ("Checking environment file", check_env_file),
        ("Creating directories", create_directories),
        ("Testing imports", test_imports),
    ]
    
    for step_name, step_func in steps:
        logger.info(f"\n{'='*60}")
        logger.info(f"Step: {step_name}")
        logger.info(f"{'='*60}\n")
        
        if not step_func():
            logger.error(f"Setup failed at: {step_name}")
            logger.info("Please fix the errors and run setup again.")
            sys.exit(1)
    
    print_summary()
    logger.success("\n✅ Setup completed successfully!")


if __name__ == "__main__":
    main()

"""
Ultron - AI Academic Assistant
Main entry point for the application
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from loguru import logger
from src.config.settings import settings
from src.dashboard.app import create_app
from src.telegram_bot.bot import UltronBot
from src.scheduler.task_scheduler import TaskScheduler


async def main():
    """Main application entry point"""
    logger.info("🤖 Starting Ultron - AI Academic Assistant")
    
    # Initialize components
    logger.info("Initializing components...")
    
    # Start scheduler for reminders and periodic tasks
    scheduler = TaskScheduler()
    scheduler.start()
    logger.info("✓ Task scheduler started")
    
    # Start Telegram bot
    telegram_bot = UltronBot()
    bot_task = asyncio.create_task(telegram_bot.start())
    logger.info("✓ Telegram bot started")
    
    # Start web dashboard
    logger.info(f"✓ Dashboard will be available at http://{settings.DASHBOARD_HOST}:{settings.DASHBOARD_PORT}")
    logger.info("=" * 50)
    logger.info("Ultron is now running!")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 50)
    
    # Run dashboard (blocking)
    import uvicorn
    config = uvicorn.Config(
        create_app(),
        host=settings.DASHBOARD_HOST,
        port=settings.DASHBOARD_PORT,
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        scheduler.shutdown()
        await telegram_bot.stop()


def run():
    """Run the application"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise


if __name__ == "__main__":
    run()

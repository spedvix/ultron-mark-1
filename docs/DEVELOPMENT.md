# Ultron Development Guide

## Project Architecture

### Overview

Ultron is built with a modular architecture consisting of:

```
┌─────────────────────────────────────────────┐
│           Main Application (main.py)        │
└───────┬─────────────────────────────────────┘
        │
        ├──► Task Scheduler (Periodic Tasks)
        ├──► Telegram Bot (User Interface)
        └──► Web Dashboard (Visual Interface)
                │
                ├──► Notion Integration (Data Source)
                ├──► Selenium Scraper (Announcements)
                ├──► AI Handler (Chat & Consultancy)
                └──► NightCrawler Client (Research)
```

## Module Documentation

### 1. Scraper Module (`src/scraper/`)

**Purpose**: Scrape university website for announcements using Selenium

**Key Files**:
- `announcement_scraper.py`: Main scraper class

**Customization**:
```python
# Update selectors in announcement_scraper.py
username_field = wait.until(
    EC.presence_of_element_located((By.ID, "your_field_id"))
)
```

**Usage**:
```python
from src.scraper import AnnouncementScraper

scraper = AnnouncementScraper()
announcements = scraper.scrape()
```

### 2. Notion Module (`src/notion/`)

**Purpose**: Interface with Notion API for accessing academic data

**Key Files**:
- `notion_manager.py`: Notion API wrapper

**Methods**:
- `get_classes()`: Retrieve all classes
- `get_assignments()`: Get upcoming assignments
- `get_exams()`: Get upcoming exams
- `get_weekly_schedule()`: Get organized weekly schedule
- `get_class_notes()`: Retrieve notes for a specific class

**Usage**:
```python
from src.notion import NotionManager

notion = NotionManager()
assignments = notion.get_assignments(upcoming_only=True)
```

### 3. Telegram Bot Module (`src/telegram_bot/`)

**Purpose**: Provide chat interface and send notifications

**Key Files**:
- `bot.py`: Telegram bot implementation

**Commands**:
- `/start`: Show main menu
- `/help`: Display help
- `/assignments`: View assignments
- `/exams`: View exams
- `/schedule`: View schedule
- `/announcements`: Check announcements
- `/research <topic>`: Perform research

**Adding New Commands**:
```python
async def cmd_custom(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Your custom command"""
    await update.message.reply_text("Hello!")

# Register in __init__
self.application.add_handler(CommandHandler("custom", self.cmd_custom))
```

### 4. AI Module (`src/ai/`)

**Purpose**: Handle AI-powered conversations and consultancy

**Key Files**:
- `chat_handler.py`: OpenAI integration for chat

**Methods**:
- `get_response()`: Get AI response to user message
- `get_study_strategy()`: Generate study strategies
- `analyze_academic_performance()`: Analyze grades and provide recommendations
- `get_assignment_help()`: Get help with assignments

**Usage**:
```python
from src.ai import ChatHandler

chat = ChatHandler()
response = await chat.get_response("How can I improve my study habits?")
```

### 5. Dashboard Module (`src/dashboard/`)

**Purpose**: Web interface for visual overview

**Key Files**:
- `app.py`: FastAPI application
- `templates/index.html`: Main dashboard template

**API Endpoints**:
- `GET /`: Dashboard home page
- `GET /api/assignments`: Get assignments as JSON
- `GET /api/exams`: Get exams as JSON
- `GET /api/schedule`: Get schedule as JSON
- `GET /api/announcements`: Get announcements as JSON
- `GET /health`: Health check

**Customization**:
Edit `templates/index.html` to change dashboard appearance.

### 6. Scheduler Module (`src/scheduler/`)

**Purpose**: Manage periodic tasks and reminders

**Key Files**:
- `task_scheduler.py`: APScheduler-based task manager

**Scheduled Tasks**:
- Check announcements (hourly)
- Assignment reminders (9 AM, 6 PM)
- Exam reminders (9 AM daily)
- Daily schedule (7:30 AM)
- Weekly summary (Sunday 8 PM)

**Customizing Schedule**:
```python
# Change timing
self.scheduler.add_job(
    self.check_announcements,
    CronTrigger(hour="*/2"),  # Every 2 hours instead of 1
    id="check_announcements"
)
```

### 7. Integrations Module (`src/integrations/`)

**Purpose**: Connect with external services

**Key Files**:
- `nightcrawler.py`: NightCrawler research integration

**Usage**:
```python
from src.integrations import NightCrawlerClient

client = NightCrawlerClient()
result = await client.research("machine learning", research_type="academic")
```

### 8. Database Module (`src/database/`)

**Purpose**: Local data storage

**Key Files**:
- `models.py`: SQLAlchemy models

**Models**:
- `Announcement`: Store scraped announcements
- `ConversationHistory`: Store chat history
- `Reminder`: Store reminders

### 9. Utils Module (`src/utils/`)

**Purpose**: Helper functions and utilities

**Key Functions**:
- `parse_date()`: Parse various date formats
- `days_until()`: Calculate days until date
- `calculate_gpa()`: Calculate GPA from grades
- `format_time_remaining()`: Human-readable time format

## Development Workflow

### Adding a New Feature

1. **Identify the module** where the feature belongs
2. **Create the implementation** in the appropriate file
3. **Update related modules** if needed
4. **Test the feature** independently
5. **Integrate** with the main application
6. **Update documentation**

### Example: Adding Grade Tracking

1. **Update Notion Manager** to fetch grades:
```python
def get_grades(self) -> List[Dict]:
    """Get all grades from Notion"""
    # Implementation
```

2. **Add Telegram Command**:
```python
async def cmd_grades(self, update, context):
    grades = self.notion.get_grades()
    # Format and send
```

3. **Add Dashboard Section**:
```python
@app.get("/api/grades")
async def get_grades():
    return {"grades": notion.get_grades()}
```

4. **Update UI**:
Edit `templates/index.html` to display grades

## Testing

### Unit Testing

Create test files in `tests/` directory:

```python
# tests/test_notion.py
import pytest
from src.notion import NotionManager

def test_get_classes():
    notion = NotionManager()
    classes = notion.get_classes()
    assert isinstance(classes, list)
```

Run tests:
```powershell
pytest tests/
```

### Manual Testing

Test individual components:

```powershell
# Test Notion
python src/notion/notion_manager.py

# Test Scraper
python src/scraper/announcement_scraper.py

# Test Bot
python src/telegram_bot/bot.py
```

## Best Practices

### 1. Configuration Management

Always use `settings` for configuration:
```python
from src.config.settings import settings

url = settings.UNI_WEBSITE_URL
```

### 2. Logging

Use loguru for logging:
```python
from loguru import logger

logger.info("Operation successful")
logger.error("Operation failed")
```

### 3. Error Handling

Always handle exceptions:
```python
try:
    result = operation()
except Exception as e:
    logger.error(f"Error: {e}")
    return default_value
```

### 4. Async/Await

Use async for I/O operations:
```python
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

### 5. Type Hints

Use type hints for better code clarity:
```python
def process_assignments(assignments: List[Dict]) -> List[str]:
    return [a["title"] for a in assignments]
```

## Deployment

### Local Deployment

1. Follow SETUP.md instructions
2. Run `python main.py`
3. Access dashboard at http://localhost:8080

### Production Deployment

For production, consider:

1. **Use environment variables** instead of .env file
2. **Set up a reverse proxy** (nginx) for the dashboard
3. **Use a process manager** (systemd, supervisor)
4. **Enable HTTPS** for the dashboard
5. **Set up monitoring** and logging
6. **Use a production database** (PostgreSQL instead of SQLite)

### Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

Build and run:
```powershell
docker build -t ultron .
docker run -d --env-file .env -p 8080:8080 ultron
```

## Troubleshooting

### Common Issues

**Issue**: Selenium can't find elements
- **Solution**: Update selectors in `announcement_scraper.py`
- **Solution**: Check if website structure changed

**Issue**: Notion API errors
- **Solution**: Verify API key and database IDs
- **Solution**: Check database sharing settings

**Issue**: Telegram bot not responding
- **Solution**: Verify bot token
- **Solution**: Check chat ID
- **Solution**: Ensure bot was started with `/start`

**Issue**: Dashboard not loading
- **Solution**: Check port availability
- **Solution**: Verify Notion credentials
- **Solution**: Check logs for errors

## Contributing

When contributing to Ultron:

1. Follow the existing code style
2. Add docstrings to new functions
3. Update documentation
4. Test your changes
5. Use meaningful commit messages

## Performance Optimization

### Tips

1. **Cache Notion data** to reduce API calls
2. **Limit scraping frequency** for announcements
3. **Use database** for frequently accessed data
4. **Optimize Selenium** with headless mode
5. **Batch Telegram messages** when sending multiple notifications

### Monitoring

Add monitoring to track:
- API response times
- Scraper success rate
- Telegram bot uptime
- Database query performance

## Security Considerations

1. **Never commit** `.env` file
2. **Use strong passwords** for university login
3. **Rotate API keys** regularly
4. **Validate user input** in chat interactions
5. **Use HTTPS** for dashboard in production
6. **Implement rate limiting** for API endpoints

## Future Enhancements

Ideas for future development:

- [ ] Mobile app integration
- [ ] Voice command support
- [ ] Study session timer with Pomodoro
- [ ] Collaborative study groups
- [ ] Grade prediction using ML
- [ ] Course recommendation system
- [ ] Integration with more university systems
- [ ] Multi-language support
- [ ] Cloud synchronization

## Resources

- [Notion API Documentation](https://developers.notion.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Review SETUP.md for configuration help
3. Check this development guide for implementation details

Happy coding! 🚀

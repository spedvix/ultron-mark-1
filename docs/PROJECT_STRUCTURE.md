# Ultron Project Structure

## Complete File Organization

```
Ultron/
│
├── 📄 README.md                    # Project overview
├── 📄 SETUP.md                     # Detailed setup instructions
├── 📄 DEVELOPMENT.md               # Developer guide
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.example                 # Environment variables template
├── 📄 .gitignore                   # Git ignore rules
├── 📄 main.py                      # Application entry point
├── 📄 setup_check.py               # Setup validation script
├── 📄 start.ps1                    # Quick start PowerShell script
│
├── 📁 src/                         # Source code
│   ├── 📄 __init__.py
│   │
│   ├── 📁 config/                  # Configuration
│   │   ├── 📄 __init__.py
│   │   └── 📄 settings.py          # Settings manager
│   │
│   ├── 📁 scraper/                 # Web scraping
│   │   ├── 📄 __init__.py
│   │   └── 📄 announcement_scraper.py
│   │
│   ├── 📁 notion/                  # Notion integration
│   │   ├── 📄 __init__.py
│   │   └── 📄 notion_manager.py
│   │
│   ├── 📁 telegram_bot/            # Telegram bot
│   │   ├── 📄 __init__.py
│   │   └── 📄 bot.py
│   │
│   ├── 📁 ai/                      # AI features
│   │   ├── 📄 __init__.py
│   │   └── 📄 chat_handler.py
│   │
│   ├── 📁 dashboard/               # Web dashboard
│   │   ├── 📄 __init__.py
│   │   ├── 📄 app.py
│   │   ├── 📁 templates/
│   │   │   ├── 📄 index.html
│   │   │   └── 📄 error.html
│   │   └── 📁 static/
│   │
│   ├── 📁 scheduler/               # Task scheduling
│   │   ├── 📄 __init__.py
│   │   └── 📄 task_scheduler.py
│   │
│   ├── 📁 integrations/            # External services
│   │   ├── 📄 __init__.py
│   │   └── 📄 nightcrawler.py
│   │
│   ├── 📁 database/                # Database models
│   │   ├── 📄 __init__.py
│   │   └── 📄 models.py
│   │
│   └── 📁 utils/                   # Utilities
│       ├── 📄 __init__.py
│       └── 📄 helpers.py
│
├── 📁 data/                        # Local data storage (created at runtime)
│   └── ultron.db
│
├── 📁 logs/                        # Application logs (created at runtime)
│   └── *.log
│
└── 📁 tests/                       # Unit tests (optional)
    └── test_*.py

```

## Key Components

### 🎯 Core Application (main.py)

Entry point that orchestrates all components:
- Initializes task scheduler
- Starts Telegram bot
- Launches web dashboard

### ⚙️ Configuration (src/config/)

Centralized settings management:
- Environment variables
- API keys
- Database configuration
- Application settings

### 🔍 Web Scraper (src/scraper/)

Selenium-based scraper:
- Login to university website
- Extract announcements
- Parse and structure data
- Detect new announcements

### 📚 Notion Integration (src/notion/)

Notion API wrapper:
- Fetch classes and schedules
- Retrieve assignments
- Get exam information
- Access class notes and syllabus

### 💬 Telegram Bot (src/telegram_bot/)

User interaction interface:
- Command handlers
- Natural language chat
- File/image handling
- Notifications and reminders

### 🤖 AI Handler (src/ai/)

OpenAI-powered features:
- Natural conversation
- Study strategy generation
- Academic consultancy
- Performance analysis

### 📊 Web Dashboard (src/dashboard/)

FastAPI web interface:
- Visual overview
- Assignment tracking
- Exam calendar
- Weekly schedule
- REST API endpoints

### ⏰ Task Scheduler (src/scheduler/)

Automated periodic tasks:
- Check announcements (hourly)
- Send reminders (daily)
- Daily schedule (morning)
- Weekly summary (Sunday)

### 🔗 Integrations (src/integrations/)

External service connectors:
- NightCrawler (research)
- Future integrations

### 💾 Database (src/database/)

SQLite database:
- Store announcements
- Conversation history
- Reminders

### 🛠️ Utilities (src/utils/)

Helper functions:
- Date parsing
- GPA calculation
- Text formatting
- Time calculations

## Data Flow

### 1. Announcement Flow
```
University Website 
    ↓ (Selenium Scraper)
Announcements Data 
    ↓ (Task Scheduler)
Database Storage
    ↓ (Telegram Bot)
User Notification
```

### 2. Assignment Reminder Flow
```
Notion Database
    ↓ (Notion Manager)
Assignment Data
    ↓ (Task Scheduler)
Check Due Dates
    ↓ (Telegram Bot)
Send Reminder
```

### 3. Chat Interaction Flow
```
User Message (Telegram)
    ↓ (Telegram Bot)
Chat Handler
    ↓ (OpenAI API)
AI Response
    ↓ (Telegram Bot)
User Reply
```

### 4. Dashboard Display Flow
```
User Request (Browser)
    ↓ (FastAPI)
Notion Manager
    ↓ (Notion API)
Fetch Data
    ↓ (Jinja2 Template)
Render HTML
```

## Technology Stack

### Backend
- **Python 3.10+**: Main language
- **FastAPI**: Web framework
- **SQLAlchemy**: Database ORM
- **APScheduler**: Task scheduling

### Integrations
- **Selenium**: Web scraping
- **Notion API**: Data source
- **Telegram Bot API**: User interface
- **OpenAI API**: AI features

### Frontend
- **HTML/CSS**: Dashboard UI
- **Jinja2**: Template engine

### Development
- **loguru**: Logging
- **python-dotenv**: Environment management
- **aiohttp**: Async HTTP client

## Feature Matrix

| Feature | Module | Status | Notes |
|---------|--------|--------|-------|
| University Announcements | Scraper | ✅ Ready | Needs selector customization |
| Notion Classes | Notion | ✅ Ready | Requires Notion setup |
| Notion Assignments | Notion | ✅ Ready | Requires Notion setup |
| Notion Exams | Notion | ✅ Ready | Requires Notion setup |
| Weekly Schedule | Notion | ✅ Ready | Requires Notion setup |
| Telegram Commands | Bot | ✅ Ready | Requires bot token |
| Chat Feature | AI | ✅ Ready | Requires OpenAI key |
| Assignment Reminders | Scheduler | ✅ Ready | Automatic |
| Exam Reminders | Scheduler | ✅ Ready | Automatic |
| Daily Schedule | Scheduler | ✅ Ready | Automatic |
| Weekly Summary | Scheduler | ✅ Ready | Automatic |
| Web Dashboard | Dashboard | ✅ Ready | http://localhost:8080 |
| NightCrawler Research | Integrations | ✅ Ready | Needs NightCrawler setup |
| Study Strategies | AI | ✅ Ready | Via chat |
| Academic Consultancy | AI | ✅ Ready | Via chat |
| GPA Tracking | Utils | ⚠️ Partial | Helper functions ready |
| File Analysis | Bot | 🔄 Planned | Coming soon |
| Voice Commands | - | 🔄 Planned | Future |

## Environment Variables Required

| Variable | Purpose | Required | Example |
|----------|---------|----------|---------|
| UNI_WEBSITE_URL | University website | ✅ Yes | https://university.edu |
| UNI_USERNAME | Login username | ✅ Yes | student@university.edu |
| UNI_PASSWORD | Login password | ✅ Yes | your_password |
| NOTION_API_KEY | Notion integration | ✅ Yes | secret_xxx |
| NOTION_DATABASE_ID | Classes/assignments DB | ✅ Yes | xxx-xxx-xxx |
| NOTION_CALENDAR_ID | Exams calendar | ✅ Yes | xxx-xxx-xxx |
| TELEGRAM_BOT_TOKEN | Telegram bot | ✅ Yes | 123456:ABC-DEF |
| TELEGRAM_CHAT_ID | Your chat ID | ✅ Yes | 123456789 |
| OPENAI_API_KEY | OpenAI API | ✅ Yes | sk-xxx |
| ANTHROPIC_API_KEY | Anthropic API | ❌ No | sk-ant-xxx |
| NIGHTCRAWLER_API_URL | Research service | ❌ No | http://localhost:8000 |
| NIGHTCRAWLER_API_KEY | Research API key | ❌ No | your_key |

## Quick Start Commands

```powershell
# Clone/Navigate to project
cd "c:\Users\speda\OneDrive\Belgeler\Projects\Ultron"

# Quick start with script
.\start.ps1

# Or manual setup
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env with your credentials
python setup_check.py
python main.py
```

## API Endpoints

### Dashboard API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard home page |
| `/api/assignments` | GET | Get assignments as JSON |
| `/api/exams` | GET | Get exams as JSON |
| `/api/schedule` | GET | Get schedule as JSON |
| `/api/announcements` | GET | Get announcements as JSON |
| `/health` | GET | Health check |

## Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Show main menu with quick actions |
| `/help` | Display help and available commands |
| `/assignments` | View upcoming assignments |
| `/exams` | View upcoming exams |
| `/schedule` | View weekly class schedule |
| `/announcements` | Check latest university announcements |
| `/research <topic>` | Perform deep research on a topic |

## Scheduled Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| Check Announcements | Every hour | Scrape university website |
| Assignment Reminders | 9 AM, 6 PM | Check for upcoming assignments |
| Exam Reminders | 9 AM daily | Check for upcoming exams |
| Daily Schedule | 7:30 AM | Send today's class schedule |
| Weekly Summary | Sunday 8 PM | Send week overview |

## Development Tips

### Running Individual Components

```powershell
# Test Notion integration
python src/notion/notion_manager.py

# Test announcement scraper
python src/scraper/announcement_scraper.py

# Test Telegram bot only
python src/telegram_bot/bot.py

# Test dashboard only
python src/dashboard/app.py

# Test scheduler only
python src/scheduler/task_scheduler.py
```

### Debugging

Enable verbose logging in `.env`:
```
LOG_LEVEL=DEBUG
```

Check logs:
```powershell
Get-Content logs/*.log -Tail 50
```

## Customization Guide

### Change Reminder Times

Edit `src/scheduler/task_scheduler.py`:
```python
# Change from 9 AM to 8 AM
CronTrigger(hour="8")
```

### Add New Telegram Command

Edit `src/telegram_bot/bot.py`:
```python
async def cmd_new(self, update, context):
    await update.message.reply_text("New command!")

# Register in __init__
self.application.add_handler(CommandHandler("new", self.cmd_new))
```

### Customize Dashboard

Edit `src/dashboard/templates/index.html` to change appearance.

### Add New Notion Properties

Edit `src/notion/notion_manager.py` to handle new properties:
```python
"new_field": self._get_property_value(properties, "New Field")
```

## Maintenance

### Regular Tasks

- **Weekly**: Check logs for errors
- **Monthly**: Update dependencies (`pip install --upgrade -r requirements.txt`)
- **As needed**: Update university website selectors if structure changes
- **As needed**: Rotate API keys for security

### Backup

Backup important files:
- `.env` (keep secure!)
- `data/ultron.db`
- Custom modifications to source code

## Support & Resources

### Documentation
- README.md - Project overview
- SETUP.md - Setup instructions
- DEVELOPMENT.md - Developer guide
- This file - Complete project structure

### Logs
- Check `logs/` directory for detailed error messages
- Enable DEBUG logging for troubleshooting

### Community
- Create GitHub issues for bugs
- Fork and submit pull requests for improvements

## Version History

- **v1.0.0** (Current) - Initial release with all core features

## License

MIT License - Feel free to modify and distribute

---

Built with ❤️ for academic excellence 🎓

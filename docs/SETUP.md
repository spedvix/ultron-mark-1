# Ultron Setup Guide

Welcome to Ultron! This guide will help you set up your AI Academic Assistant.

## Prerequisites

- Python 3.10 or higher
- Google Chrome browser (for Selenium)
- A Notion account with API access
- A Telegram bot token
- OpenAI API key

## Step-by-Step Setup

### 1. Install Python Dependencies

```powershell
cd "c:\Users\speda\OneDrive\Belgeler\Projects\Ultron"
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Edit `.env` file and fill in your credentials:

#### University Website
- `UNI_WEBSITE_URL`: Your university's website URL
- `UNI_USERNAME`: Your university login username
- `UNI_PASSWORD`: Your university login password

#### Notion Setup

1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Name it "Ultron" and select your workspace
4. Copy the "Internal Integration Token" to `NOTION_API_KEY`

5. Set up your Notion databases:
   - Create a database for classes with columns: Name, Instructor, Schedule, Room
   - Create a database for assignments with columns: Name, Class, Due Date, Status, Priority, Description
   - Create a calendar for exams with properties: Name, Class, Date, Exam Type, Location
   
6. Share these databases with your integration:
   - Open each database
   - Click "..." → "Add connections" → Select "Ultron"
   
7. Get database IDs from the URL:
   - Open database → Copy the URL
   - Format: `https://notion.so/{workspace}/{database_id}?v=...`
   - Copy the `database_id` part to `NOTION_DATABASE_ID` and `NOTION_CALENDAR_ID`

#### Telegram Bot Setup

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the bot token to `TELEGRAM_BOT_TOKEN`
5. Start a chat with your new bot
6. Get your chat ID:
   - Send a message to your bot
   - Visit: `https://api.telegram.org/bot<YourBOTToken>/getUpdates`
   - Find `"chat":{"id":123456789}` in the response
   - Copy the ID to `TELEGRAM_CHAT_ID`

#### OpenAI API

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy it to `OPENAI_API_KEY`

#### NightCrawler (Optional)

If you have NightCrawler running:
- Set `NIGHTCRAWLER_API_URL` to your NightCrawler instance URL
- Set `NIGHTCRAWLER_API_KEY` to your API key

### 3. Initialize Database

```powershell
python -c "from src.database.models import init_db; init_db()"
```

### 4. Update Selenium Selectors

Open `src/scraper/announcement_scraper.py` and update the selectors to match your university's website structure:

```python
# Update these lines based on your university's HTML structure
username_field = wait.until(
    EC.presence_of_element_located((By.ID, "username"))  # Change "username" to your field ID
)
password_field = self.driver.find_element(By.ID, "password")  # Change "password"
submit_button = self.driver.find_element(By.ID, "submit")  # Change "submit"
```

### 5. Run Ultron

```powershell
python main.py
```

This will start:
- ✅ Task scheduler (for reminders and periodic checks)
- ✅ Telegram bot (for chat and notifications)
- ✅ Web dashboard at http://localhost:8080

## Testing Individual Components

### Test Notion Integration
```powershell
python src/notion/notion_manager.py
```

### Test Announcement Scraper
```powershell
python src/scraper/announcement_scraper.py
```

### Test Telegram Bot
```powershell
python src/telegram_bot/bot.py
```

### Test Dashboard Only
```powershell
python src/dashboard/app.py
```

## Using Ultron

### Telegram Commands

- `/start` - Show main menu
- `/help` - Display help information
- `/assignments` - View upcoming assignments
- `/exams` - View upcoming exams
- `/schedule` - View weekly schedule
- `/announcements` - Check university announcements
- `/research <topic>` - Perform deep research

You can also just chat naturally with Ultron!

### Web Dashboard

Access the dashboard at http://localhost:8080 to see:
- 📊 Overview statistics
- 📚 Upcoming assignments
- 📝 Upcoming exams
- 📅 Today's classes
- 📅 Weekly schedule

### Automated Reminders

Ultron will automatically:
- ✅ Check for announcements every hour
- ✅ Send assignment reminders (7, 3, 1 day before due)
- ✅ Send exam reminders (14, 7, 3, 1 day before)
- ✅ Send daily schedule every morning at 7:30 AM
- ✅ Send weekly summary every Sunday at 8 PM

## Troubleshooting

### Selenium Issues

If Chrome driver fails:
```powershell
pip install --upgrade selenium webdriver-manager
```

### Notion API Issues

- Ensure databases are shared with your integration
- Check that database IDs are correct
- Verify API key is valid

### Telegram Bot Not Responding

- Verify bot token is correct
- Check that you've started a chat with your bot
- Ensure chat ID is correct

### Dashboard Not Loading

- Check if port 8080 is available
- Look for errors in console output
- Verify Notion credentials are set

## Customization

### Change Dashboard Port

Edit `.env`:
```
DASHBOARD_PORT=3000
```

### Adjust Reminder Schedule

Edit `src/scheduler/task_scheduler.py` and modify `CronTrigger` parameters:

```python
# Daily at 8 AM instead of 7:30 AM
self.scheduler.add_job(
    self.send_daily_schedule,
    CronTrigger(hour="8", minute="0"),
    id="daily_schedule"
)
```

### Add Custom Commands

Edit `src/telegram_bot/bot.py` and add new command handlers:

```python
async def cmd_custom(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Custom command!")

# Register in __init__
self.application.add_handler(CommandHandler("custom", self.cmd_custom))
```

## Security Notes

- ⚠️ Never commit `.env` file to version control
- ⚠️ Keep API keys secure
- ⚠️ Use strong passwords for university login
- ⚠️ Consider using environment variables instead of `.env` in production

## Need Help?

Check the logs in `logs/` directory for detailed error messages.

## Future Enhancements

- [ ] GPA tracking and calculations
- [ ] Study session timer
- [ ] Pomodoro technique integration
- [ ] Grade predictions
- [ ] Course recommendations
- [ ] Study group coordination
- [ ] Mobile app integration
- [ ] Voice commands

Enjoy using Ultron! 🤖

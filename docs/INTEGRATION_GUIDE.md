# 🔗 Ultron Integration Setup Guide

This guide will help you set up all the necessary integrations for your Ultron AI Academic Assistant.

---

## 📋 Required Integrations

### 1. ✅ OpenAI API (REQUIRED for Chat System)

**What it does:** Powers the AI chat interface with GPT-4o

**Steps to get API key:**

1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to **API keys** (https://platform.openai.com/api-keys)
4. Click **"Create new secret key"**
5. Copy the key (starts with `sk-...`)
6. Add to `.env`:
   ```env
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

**Cost:** 
- Text chat: ~$0.005 per message
- Image analysis: ~$0.01 per image
- Estimated: $5-20/month for normal use

**Test it:**
```powershell
python test_chat_system.py
```

---

### 2. 📚 Notion Integration (REQUIRED for Academic Data)

**What it does:** Syncs your assignments, exams, classes, and schedule

**Steps to set up:**

#### Step 1: Create a Notion Integration

1. Go to https://www.notion.so/my-integrations
2. Click **"+ New integration"**
3. Name it "Ultron Assistant"
4. Select your workspace
5. Click **"Submit"**
6. Copy the **Internal Integration Token** (starts with `secret_...`)
7. Add to `.env`:
   ```env
   NOTION_API_KEY=secret_your-token-here
   ```

#### Step 2: Set Up Your Notion Databases

You need **two databases** in Notion:

**A. Assignments/Tasks Database**

Create a database with these properties:
- **Name** (Title) - Assignment name
- **Description** (Text) - Assignment details
- **Due Date** (Date) - When it's due
- **Class** (Select or Text) - Which class
- **Status** (Select) - Not Started, In Progress, Completed

**B. Classes/Schedule Database**

Create a database with these properties:
- **Name** (Title) - Class name
- **Instructor** (Text) - Professor name
- **Schedule** (Text) - Day and time (e.g., "Mon/Wed 10:00-11:30")
- **Room** (Text) - Location

#### Step 3: Share Databases with Integration

For EACH database:
1. Open the database in Notion
2. Click **"..."** (three dots) → **"Add connections"**
3. Search for **"Ultron Assistant"**
4. Click to connect

#### Step 4: Get Database IDs

For EACH database:
1. Open the database as a full page
2. Look at the URL: `https://notion.so/yourworkspace/DATABASE_ID?v=...`
3. Copy the `DATABASE_ID` (32-character code between the last `/` and `?`)
4. Add to `.env`:
   ```env
   NOTION_DATABASE_ID=your-assignments-database-id-here
   NOTION_CALENDAR_ID=your-classes-database-id-here
   ```

**Example URL:**
```
https://www.notion.so/workspace/a1b2c3d4e5f6789012345678901234?v=...
                                └─────────────────────────┘
                                    This is your ID
```

**Test it:**
```powershell
python -c "from src.notion.notion_manager import NotionManager; nm = NotionManager(); print(nm.get_classes())"
```

---

### 3. 🤖 Telegram Bot (OPTIONAL)

**What it does:** Send reminders and notifications via Telegram

**Steps to set up:**

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Follow instructions to name your bot
4. Copy the **API token** (looks like `123456:ABC-DEF...`)
5. Add to `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=your-bot-token-here
   ```

**Get your Chat ID:**
1. Search for **@userinfobot** in Telegram
2. Send `/start`
3. Copy your **ID** (a number)
4. Add to `.env`:
   ```env
   TELEGRAM_CHAT_ID=your-chat-id-here
   ```

**Test it:**
```powershell
python -c "from src.telegram_bot.bot import UltronBot; import asyncio; bot = UltronBot(); asyncio.run(bot.test_connection())"
```

---

### 4. 🌐 University Website Scraper (OPTIONAL)

**What it does:** Automatically scrapes announcements from your university website

**Setup:**

1. Find your university's announcement page URL
2. Add to `.env`:
   ```env
   UNI_WEBSITE_URL=https://your-university.edu/announcements
   UNI_USERNAME=your-student-id
   UNI_PASSWORD=your-password
   ```

⚠️ **Security Note:** Your password is stored locally in `.env` (never shared)

**Test it:**
```powershell
python -c "from src.scraper.announcement_scraper import AnnouncementScraper; scraper = AnnouncementScraper(); print(scraper.scrape())"
```

---

## 🚀 Quick Start After Setup

### Minimum Required Setup:
1. ✅ **OpenAI API Key** (for chat)
2. ✅ **Notion Integration** (for academic data)

### Start Ultron:
```powershell
python main.py
```

### Access:
- **Main Dashboard:** http://localhost:8080
- **AI Chat:** http://localhost:8080/chat

---

## 🧪 Testing Your Integrations

### Test Everything at Once:
```powershell
python test_chat_system.py
```

### Test Individual Components:

**OpenAI:**
```powershell
python -c "from openai import OpenAI; client = OpenAI(); print('OpenAI: OK')"
```

**Notion:**
```powershell
python -c "from src.notion.notion_manager import NotionManager; nm = NotionManager(); print('Classes:', len(nm.get_classes())); print('Assignments:', len(nm.get_assignments()))"
```

**Dashboard:**
```powershell
python main.py
# Then visit http://localhost:8080
```

---

## 📝 Sample Notion Setup

### Example Assignments Database:

| Name | Description | Due Date | Class | Status |
|------|-------------|----------|-------|--------|
| Calculus Homework 5 | Chapter 8 problems | Oct 25 | MATH 201 | In Progress |
| Essay on Shakespeare | 1500 words | Oct 28 | ENG 101 | Not Started |
| Lab Report 3 | Physics experiment | Oct 30 | PHYS 150 | Completed |

### Example Classes Database:

| Name | Instructor | Schedule | Room |
|------|-----------|----------|------|
| Calculus II | Dr. Smith | Mon/Wed 10:00-11:30 | SC-204 |
| English Literature | Prof. Johnson | Tue/Thu 14:00-15:30 | HU-101 |
| Physics Lab | Dr. Brown | Fri 13:00-16:00 | LAB-3 |

---

## 🔧 Troubleshooting

### "OpenAI API Error"
- ✅ Check API key is correct
- ✅ Verify you have credits: https://platform.openai.com/account/usage
- ✅ Check internet connection

### "Notion Connection Failed"
- ✅ Verify integration token is correct
- ✅ Make sure databases are shared with integration
- ✅ Check database IDs are correct (32-character codes)
- ✅ Ensure database properties match expected names

### "No Classes/Assignments Found"
- ✅ Add some sample data to your Notion databases
- ✅ Make sure databases have the required properties
- ✅ Check that integration has access to databases

### "Telegram Bot Not Responding"
- ✅ Verify bot token is correct
- ✅ Make sure you've started the bot (send `/start` in Telegram)
- ✅ Check chat ID is correct

---

## 🎯 Next Steps After Integration

1. **Add Your Academic Data to Notion**
   - Import your classes
   - Add upcoming assignments
   - Set up your schedule

2. **Test the Chat Interface**
   - Visit http://localhost:8080/chat
   - Try asking: "What assignments do I have?"
   - Try: "How many days until my exam?"

3. **Explore Features**
   - Upload images for analysis
   - Ask questions about your schedule
   - Use web search for research

---

## 📞 Getting Help

If you're stuck:

1. **Check logs:** Look at the terminal output for error messages
2. **Verify .env:** Make sure all required keys are filled in
3. **Test individually:** Use the test commands above
4. **Check documentation:** 
   - OpenAI: https://platform.openai.com/docs
   - Notion: https://developers.notion.com/docs

---

## 🔒 Security Best Practices

- ✅ Never commit `.env` file to git
- ✅ Keep API keys secret
- ✅ Regularly rotate API keys
- ✅ Use read-only access where possible
- ✅ Monitor API usage and costs

---

**Ready to get started? Follow the steps above and you'll have Ultron fully integrated in 10-15 minutes!** 🚀

# Testing the Dashboard

There are several ways to test the Ultron dashboard:

## Option 1: Quick Test (Without Dependencies)

Test just the dashboard structure:

```powershell
cd "c:\Users\speda\OneDrive\Belgeler\Projects\Ultron"

# Check if files exist
Test-Path src\dashboard\app.py
Test-Path src\dashboard\templates\index.html
```

## Option 2: Install Dependencies First

Install all required packages:

```powershell
cd "c:\Users\speda\OneDrive\Belgeler\Projects\Ultron"

# Install dependencies
pip install -r requirements.txt

# Run the dashboard test
python test_dashboard.py
```

This will:
1. ✅ Check FastAPI installation
2. ✅ Verify template files
3. ✅ Import dashboard app
4. ✅ List available endpoints
5. 🚀 Start the server at http://localhost:8080

## Option 3: Test with Mock Data (No Notion Required)

Create a test version that doesn't need Notion:

```powershell
# Run dashboard with mock data
python test_dashboard_mock.py
```

## Option 4: Full Integration Test

After configuring .env with all credentials:

```powershell
# Run the complete application
python main.py
```

Then open your browser to http://localhost:8080

## Quick Installation

If you haven't installed dependencies yet:

```powershell
# Install Python packages
pip install fastapi uvicorn jinja2 notion-client selenium python-telegram-bot openai apscheduler sqlalchemy loguru python-dotenv pydantic-settings aiohttp requests beautifulsoup4 webdriver-manager anthropic

# Or install from requirements.txt
pip install -r requirements.txt
```

## Testing Individual Components

### Test Dashboard Only (Standalone)

```powershell
# Start just the dashboard server
python -c "from src.dashboard.app import create_app; import uvicorn; uvicorn.run(create_app(), host='0.0.0.0', port=8080)"
```

### Test API Endpoints

Once the dashboard is running, test endpoints:

```powershell
# Health check
curl http://localhost:8080/health

# Get assignments
curl http://localhost:8080/api/assignments

# Get exams
curl http://localhost:8080/api/exams

# Get schedule
curl http://localhost:8080/api/schedule
```

Or open in browser:
- http://localhost:8080/ (Main dashboard)
- http://localhost:8080/health (Health check)
- http://localhost:8080/api/assignments (JSON data)

## What You'll See

### Dashboard Home Page
- 📊 Statistics cards (assignments, exams, classes, GPA)
- 📚 Upcoming assignments list
- 📝 Upcoming exams
- 📅 Today's classes
- 📅 Weekly schedule

### Without Notion Setup
If Notion isn't configured, you'll see:
- Empty lists with "No data" messages
- The dashboard will still load and display the UI

### With Notion Setup
If Notion is configured, you'll see:
- Real data from your Notion databases
- Live assignments and exams
- Your actual class schedule

## Troubleshooting

### Error: "No module named 'fastapi'"
**Solution**: Install FastAPI
```powershell
pip install fastapi uvicorn
```

### Error: "No module named 'notion_client'"
**Solution**: Install all dependencies
```powershell
pip install -r requirements.txt
```

### Error: Port 8080 already in use
**Solution**: Use a different port
```powershell
# Edit .env file
DASHBOARD_PORT=3000
```

### Error: Template not found
**Solution**: Make sure you're in the project root directory
```powershell
cd "c:\Users\speda\OneDrive\Belgeler\Projects\Ultron"
```

### Dashboard shows no data
**Solution**: Check your Notion credentials in .env file

## Browser Testing Checklist

Once the dashboard is running at http://localhost:8080:

- [ ] Home page loads
- [ ] Statistics cards display
- [ ] Assignments section shows (even if empty)
- [ ] Exams section shows (even if empty)
- [ ] Schedule section shows (even if empty)
- [ ] Page is responsive (try resizing window)
- [ ] No console errors (press F12 in browser)

## API Testing with Postman/Insomnia

You can also test the API endpoints using tools like:

1. **Postman** - Download from https://www.postman.com/
2. **Insomnia** - Download from https://insomnia.rest/
3. **curl** - Built into PowerShell

Example API tests:

```powershell
# GET health check
Invoke-WebRequest -Uri "http://localhost:8080/health" | Select-Object -Expand Content

# GET assignments
Invoke-WebRequest -Uri "http://localhost:8080/api/assignments" | Select-Object -Expand Content

# GET schedule
Invoke-WebRequest -Uri "http://localhost:8080/api/schedule" | Select-Object -Expand Content
```

## Next Steps

After successful testing:

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Configure .env file with your credentials
3. ✅ Run setup check: `python setup_check.py`
4. ✅ Start full application: `python main.py`
5. ✅ Open dashboard: http://localhost:8080
6. ✅ Test Telegram bot commands
7. ✅ Verify automated reminders

Enjoy testing Ultron! 🚀

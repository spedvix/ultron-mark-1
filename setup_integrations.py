"""
Interactive setup script for Ultron integrations
"""
import os
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")


def print_step(number, text):
    """Print a step number"""
    print(f"\n🔹 Step {number}: {text}")


def get_input(prompt, required=True, secret=False):
    """Get user input with optional requirement"""
    while True:
        if secret:
            value = input(f"   {prompt}: ").strip()
        else:
            value = input(f"   {prompt}: ").strip()
        
        if value or not required:
            return value
        print("   ⚠️  This field is required. Please enter a value.")


def test_openai(api_key):
    """Test OpenAI connection"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        # Simple test
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_completion_tokens=5
        )
        return True, "✅ OpenAI connection successful!"
    except Exception as e:
        return False, f"❌ OpenAI connection failed: {str(e)}"


def test_notion(api_key):
    """Test Notion connection"""
    try:
        from notion_client import Client
        client = Client(auth=api_key)
        # Test connection
        client.users.me()
        return True, "✅ Notion connection successful!"
    except Exception as e:
        return False, f"❌ Notion connection failed: {str(e)}"


def main():
    print_header("🚀 ULTRON INTEGRATION SETUP")
    print("This wizard will help you set up all integrations for Ultron.\n")
    print("You'll need:")
    print("  • OpenAI API Key (REQUIRED)")
    print("  • Notion Integration Token (REQUIRED)")
    print("  • Notion Database IDs (REQUIRED)")
    print("  • Telegram Bot Token (OPTIONAL)")
    
    input("\nPress Enter to continue...")
    
    # Load existing .env if it exists
    env_path = Path(".env")
    env_vars = {}
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    
    # Setup OpenAI
    print_header("1️⃣  OpenAI API Setup")
    print("OpenAI powers the AI chat interface.\n")
    print("📍 Get your API key:")
    print("   1. Visit https://platform.openai.com/api-keys")
    print("   2. Click 'Create new secret key'")
    print("   3. Copy the key (starts with 'sk-')\n")
    
    openai_key = get_input("Enter your OpenAI API key", required=True, secret=True)
    
    print("\n🧪 Testing OpenAI connection...")
    success, message = test_openai(openai_key)
    print(message)
    
    if success:
        env_vars['OPENAI_API_KEY'] = openai_key
    else:
        print("\n⚠️  OpenAI test failed, but continuing. You can fix this later.")
        retry = input("Do you want to try a different key? (y/n): ").lower()
        if retry == 'y':
            openai_key = get_input("Enter your OpenAI API key", required=True, secret=True)
        env_vars['OPENAI_API_KEY'] = openai_key
    
    # Setup Notion
    print_header("2️⃣  Notion Integration Setup")
    print("Notion stores your academic data (assignments, exams, classes).\n")
    print("📍 Get your integration token:")
    print("   1. Visit https://www.notion.so/my-integrations")
    print("   2. Click '+ New integration'")
    print("   3. Name it 'Ultron Assistant'")
    print("   4. Copy the 'Internal Integration Token' (starts with 'secret_')\n")
    
    notion_key = get_input("Enter your Notion integration token", required=True, secret=True)
    
    print("\n🧪 Testing Notion connection...")
    success, message = test_notion(notion_key)
    print(message)
    
    if success:
        env_vars['NOTION_API_KEY'] = notion_key
    else:
        print("\n⚠️  Notion test failed, but continuing. You can fix this later.")
        env_vars['NOTION_API_KEY'] = notion_key
    
    # Notion Database IDs
    print("\n📚 Now we need your Notion database IDs.\n")
    print("📍 To get a database ID:")
    print("   1. Open your database as a full page in Notion")
    print("   2. Look at the URL: notion.so/workspace/DATABASE_ID?v=...")
    print("   3. Copy the 32-character code between the last '/' and '?'\n")
    
    print("You need TWO databases:")
    print("   A. Assignments/Tasks database")
    print("   B. Classes/Schedule database\n")
    
    assignments_db = get_input("Enter Assignments Database ID", required=True)
    env_vars['NOTION_DATABASE_ID'] = assignments_db
    
    classes_db = get_input("Enter Classes Database ID", required=True)
    env_vars['NOTION_CALENDAR_ID'] = classes_db
    
    # Optional: Google Calendar
    print_header("3) Google Calendar Setup (OPTIONAL)")
    print("Google Calendar keeps assignments, exams, and class schedules in sync across devices.\n")
    print("You'll need a Google OAuth client secret JSON (Desktop application) and the generated token JSON.")
    print("Run `python setup_google_calendar.py --credentials path/to/client_secret.json` and follow the browser flow.\n")
    
    setup_calendar = input("Do you want to configure Google Calendar now? (y/n): ").lower()
    
    if setup_calendar == "y":
        default_token = env_vars.get('GOOGLE_CALENDAR_TOKEN_FILE', 'data/google_calendar_token.json')
        token_path = get_input(f"Token JSON path [default: {default_token}]", required=False)
        env_vars['GOOGLE_CALENDAR_TOKEN_FILE'] = token_path or default_token
        
        assignments_id = get_input("Calendar ID for assignments (default: primary)", required=False)
        env_vars['GOOGLE_CALENDAR_ASSIGNMENTS_ID'] = assignments_id or env_vars.get('GOOGLE_CALENDAR_ASSIGNMENTS_ID', 'primary')
        
        exams_id = get_input("Calendar ID for exams (leave blank to reuse assignments calendar)", required=False)
        if exams_id:
            env_vars['GOOGLE_CALENDAR_EXAMS_ID'] = exams_id
        
        schedule_id = get_input("Calendar ID for weekly schedule (leave blank to reuse assignments calendar)", required=False)
        if schedule_id:
            env_vars['GOOGLE_CALENDAR_SCHEDULE_ID'] = schedule_id
        
        tz_default = env_vars.get('GOOGLE_CALENDAR_TIMEZONE', 'Europe/Istanbul')
        timezone = get_input(f"Timezone (default: {tz_default})", required=False)
        env_vars['GOOGLE_CALENDAR_TIMEZONE'] = timezone or tz_default
    
    # Optional: Telegram
    print_header("4️⃣  Telegram Bot Setup (OPTIONAL)")
    print("Telegram allows Ultron to send you notifications.\n")
    
    setup_telegram = input("Do you want to set up Telegram? (y/n): ").lower()
    
    if setup_telegram == 'y':
        print("\n📍 Get your bot token:")
        print("   1. Open Telegram and search for @BotFather")
        print("   2. Send /newbot and follow instructions")
        print("   3. Copy the API token\n")
        
        telegram_token = get_input("Enter Telegram Bot Token", required=False)
        if telegram_token:
            env_vars['TELEGRAM_BOT_TOKEN'] = telegram_token
            
            print("\n📍 Get your Chat ID:")
            print("   1. Search for @userinfobot in Telegram")
            print("   2. Send /start")
            print("   3. Copy your ID (a number)\n")
            
            telegram_chat = get_input("Enter your Telegram Chat ID", required=False)
            if telegram_chat:
                env_vars['TELEGRAM_CHAT_ID'] = telegram_chat
    
    # Optional: University Scraper
    print_header("5️⃣  University Website Scraper (OPTIONAL)")
    print("Automatically scrape announcements from your university website.\n")
    
    setup_scraper = input("Do you want to set up the scraper? (y/n): ").lower()
    
    if setup_scraper == 'y':
        uni_url = get_input("Enter your university announcement page URL", required=False)
        if uni_url:
            env_vars['UNI_WEBSITE_URL'] = uni_url
            env_vars['UNI_USERNAME'] = get_input("Enter your university username", required=False)
            env_vars['UNI_PASSWORD'] = get_input("Enter your university password", required=False, secret=True)
    
    # Fill in remaining env vars with defaults
    default_vars = {
        'DATABASE_URL': 'sqlite:///./ultron.db',
        'SECRET_KEY': 'ultron-secret-key-change-in-production',
        'DEBUG': 'True',
        'HOST': '0.0.0.0',
        'PORT': '8080',
        'SCHEDULER_ENABLED': 'True',
        'SCRAPER_INTERVAL': '3600',
        'REMINDER_ADVANCE_HOURS': '24',
        'GOOGLE_CALENDAR_TOKEN_FILE': 'data/google_calendar_token.json',
        'GOOGLE_CALENDAR_ASSIGNMENTS_ID': 'primary',
        'GOOGLE_CALENDAR_TIMEZONE': 'Europe/Istanbul',
        'LOG_LEVEL': 'INFO'
    }
    
    for key, value in default_vars.items():
        if key not in env_vars or not env_vars[key]:
            env_vars[key] = value
    
    # Write .env file
    print_header("💾 Saving Configuration")
    
    with open('.env', 'w') as f:
        f.write("# Ultron AI Academic Assistant Configuration\n")
        f.write("# Generated by setup_integrations.py\n\n")
        
        f.write("# === REQUIRED INTEGRATIONS ===\n")
        f.write(f"OPENAI_API_KEY={env_vars.get('OPENAI_API_KEY', '')}\n")
        f.write(f"NOTION_API_KEY={env_vars.get('NOTION_API_KEY', '')}\n")
        f.write(f"NOTION_DATABASE_ID={env_vars.get('NOTION_DATABASE_ID', '')}\n")
        f.write(f"NOTION_CALENDAR_ID={env_vars.get('NOTION_CALENDAR_ID', '')}\n\n")
        
        f.write("# === OPTIONAL INTEGRATIONS ===\n")
        f.write(f"TELEGRAM_BOT_TOKEN={env_vars.get('TELEGRAM_BOT_TOKEN', '')}\n")
        f.write(f"TELEGRAM_CHAT_ID={env_vars.get('TELEGRAM_CHAT_ID', '')}\n")
        f.write(f"UNI_WEBSITE_URL={env_vars.get('UNI_WEBSITE_URL', '')}\n")
        f.write(f"UNI_USERNAME={env_vars.get('UNI_USERNAME', '')}\n")
        f.write(f"UNI_PASSWORD={env_vars.get('UNI_PASSWORD', '')}\n\n")
        f.write("# === GOOGLE CALENDAR ===\n")
        f.write(f"GOOGLE_CALENDAR_TOKEN_FILE={env_vars.get('GOOGLE_CALENDAR_TOKEN_FILE', 'data/google_calendar_token.json')}\n")
        f.write(f"GOOGLE_CALENDAR_ASSIGNMENTS_ID={env_vars.get('GOOGLE_CALENDAR_ASSIGNMENTS_ID', 'primary')}\n")
        f.write(f"GOOGLE_CALENDAR_EXAMS_ID={env_vars.get('GOOGLE_CALENDAR_EXAMS_ID', '')}\n")
        f.write(f"GOOGLE_CALENDAR_SCHEDULE_ID={env_vars.get('GOOGLE_CALENDAR_SCHEDULE_ID', '')}\n")
        f.write(f"GOOGLE_CALENDAR_TIMEZONE={env_vars.get('GOOGLE_CALENDAR_TIMEZONE', 'Europe/Istanbul')}\n\n")
        
        f.write("# === SYSTEM CONFIGURATION ===\n")
        f.write(f"DATABASE_URL={env_vars.get('DATABASE_URL', '')}\n")
        f.write(f"SECRET_KEY={env_vars.get('SECRET_KEY', '')}\n")
        f.write(f"DEBUG={env_vars.get('DEBUG', '')}\n")
        f.write(f"HOST={env_vars.get('HOST', '')}\n")
        f.write(f"PORT={env_vars.get('PORT', '')}\n\n")
        
        f.write("# === SCHEDULER SETTINGS ===\n")
        f.write(f"SCHEDULER_ENABLED={env_vars.get('SCHEDULER_ENABLED', '')}\n")
        f.write(f"SCRAPER_INTERVAL={env_vars.get('SCRAPER_INTERVAL', '')}\n")
        f.write(f"REMINDER_ADVANCE_HOURS={env_vars.get('REMINDER_ADVANCE_HOURS', '')}\n\n")
        
        f.write("# === LOGGING ===\n")
        f.write(f"LOG_LEVEL={env_vars.get('LOG_LEVEL', '')}\n")
    
    print("✅ Configuration saved to .env\n")
    
    # Summary
    print_header("✨ Setup Complete!")
    print("Your integrations are configured:\n")
    print(f"  ✅ OpenAI API: {'Configured' if env_vars.get('OPENAI_API_KEY') else '❌ Missing'}")
    print(f"  ✅ Notion Integration: {'Configured' if env_vars.get('NOTION_API_KEY') else '❌ Missing'}")
    print(f"  ✅ Notion Databases: {'Configured' if env_vars.get('NOTION_DATABASE_ID') else '❌ Missing'}")
    print(f"  {'?' if env_vars.get('GOOGLE_CALENDAR_TOKEN_FILE') else '?'} Google Calendar: {'Configured' if env_vars.get('GOOGLE_CALENDAR_TOKEN_FILE') else 'Skipped (optional)'}")
    print(f"  {'✅' if env_vars.get('TELEGRAM_BOT_TOKEN') else '⚪'} Telegram Bot: {'Configured' if env_vars.get('TELEGRAM_BOT_TOKEN') else 'Skipped (optional)'}")
    print(f"  {'✅' if env_vars.get('UNI_WEBSITE_URL') else '⚪'} University Scraper: {'Configured' if env_vars.get('UNI_WEBSITE_URL') else 'Skipped (optional)'}")
    
    print("\n🚀 Next Steps:\n")
    print("  1. Add some data to your Notion databases")
    print("  2. Start Ultron: python main.py")
    print("  3. Open chat interface: http://localhost:8080/chat")
    print("  4. Test by asking: 'What assignments do I have?'\n")
    
    print("📖 For detailed setup instructions, see: INTEGRATION_GUIDE.md")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user.")
    except Exception as e:
        print(f"\n\n❌ An error occurred: {str(e)}")
        print("Please check INTEGRATION_GUIDE.md for manual setup instructions.")

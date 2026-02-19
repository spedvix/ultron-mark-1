# 🤖 Ultron AI Chat System - Quick Start Guide

## What's New?

Your Ultron dashboard now includes a **powerful AI chat interface** with:

- 🧠 **GPT-4 Powered Conversations** - Advanced AI that understands your academic needs
- 📊 **Notion Integration** - Direct access to your assignments, exams, and schedule
- 🔍 **Web Search** - Real-time information from the internet
- 🖼️ **Image Analysis** - Upload and analyze images with GPT-4 Vision
- 📄 **Document Processing** - Upload PDFs, code files, and more
- 💬 **Natural Conversations** - Ask questions in plain language

## Quick Setup (5 Minutes)

### 1. Install New Dependencies

```powershell
# Run the automated setup
python setup_chat.py
```

Or manually:
```powershell
pip install -r requirements.txt --upgrade
```

### 2. Configure OpenAI API

Add to your `.env` file:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

Get your API key from: https://platform.openai.com/api-keys

### 3. Start the Dashboard

```powershell
python main.py
```

### 4. Open Chat Interface

Navigate to: **http://localhost:8080/chat**

Or click the 🤖 button on the dashboard!

## Example Conversations

### Academic Questions

**You:** "How many assignments do I have?"
**Ultron:** *Checks Notion and lists all your assignments with due dates*

**You:** "What's due this week?"
**Ultron:** *Filters assignments by deadline and prioritizes urgent ones*

**You:** "How many days until my calculus exam?"
**Ultron:** *Calculates days remaining and provides exam details*

### Advanced Queries

**You:** "Which assignments should I finish first?"
**Ultron:** *Analyzes deadlines, prioritizes by urgency, suggests order*

**You:** "Do I have class tomorrow?"
**Ultron:** *Checks schedule and lists tomorrow's classes*

**You:** "What's my schedule for Monday?"
**Ultron:** *Provides complete Monday schedule*

### Image Analysis

1. Click "📎 Upload File"
2. Select an image (lecture slide, diagram, notes)
3. Type: "Explain this to me"
4. Ultron analyzes and explains the image

### Document Processing

1. Upload a PDF (lecture notes, textbook chapter)
2. Ask: "Summarize this for me"
3. Ultron extracts text and provides summary

### Web Search

**You:** "What's the latest news about quantum computing?"
**Ultron:** *Searches the web and provides current information*

## Chat Features

### Smart Query Understanding

The AI automatically detects what you need:
- **Notion queries** → Fetches your academic data
- **Web searches** → Searches the internet
- **General questions** → Uses AI knowledge

### File Upload Support

**Supported formats:**
- Images: JPG, PNG, GIF, BMP, WebP
- Documents: PDF
- Text: TXT, MD, PY, JS, Java, C/C++, HTML, CSS

**Max file size:** 10MB

### Conversation Memory

- Remembers last 10 messages
- Maintains context across questions
- Supports follow-up queries

## Telegram Bot (Still Available!)

The Telegram integration is **still intact**! You have two options:

1. **Web Chat** (New!) - Use the browser interface at `/chat`
2. **Telegram Bot** (Original) - Message via Telegram as before

Both use the same AI backend!

## Tips for Best Results

### Be Specific
❌ "Tell me about my classes"
✅ "What classes do I have today?"

### Use Natural Language
✅ "How many days until my final exam?"
✅ "Which homework is due tomorrow?"
✅ "Am I free this afternoon?"

### Upload Clear Files
- High-quality images work best
- PDFs should be text-based (not scanned images)
- Keep files under 10MB

### Ask Follow-Up Questions
```
You: "What exams do I have coming up?"
Ultron: [Lists exams]

You: "When is the chemistry one?"
Ultron: [Provides specific date and days remaining]
```

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│         User (Web Interface)                │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│      FastAPI Dashboard (/api/chat)          │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         Ultron Agent (LangGraph)            │
│                                             │
│  ┌──────────────────────────────────┐      │
│  │   1. Analyze Query               │      │
│  │   2. Route to Resources          │      │
│  │   3. Fetch Data (Notion/Web)     │      │
│  │   4. Generate Response           │      │
│  └──────────────────────────────────┘      │
└──────┬─────────────────┬────────────────────┘
       │                 │
       ▼                 ▼
┌─────────────┐   ┌──────────────┐
│ Notion API  │   │ Web Search   │
│  (Academic  │   │ (DuckDuckGo) │
│    Data)    │   │              │
└─────────────┘   └──────────────┘
```

## Technology Stack

- **LangChain & LangGraph** - AI orchestration and workflow
- **OpenAI GPT-4o** - Language model with vision
- **FastAPI** - Backend API
- **Notion API** - Academic data access
- **DuckDuckGo** - Web search
- **Pillow & PyPDF** - File processing

## Troubleshooting

### "OpenAI API Error"
- Check your API key in `.env`
- Verify you have API credits
- Check internet connection

### "Notion data not loading"
- Verify `NOTION_API_KEY` is set
- Check database and calendar IDs
- Ensure Notion integration has proper permissions

### "File upload fails"
- Check file size (must be < 10MB)
- Verify file format is supported
- Try a different file

### Chat is slow
- Normal response time: 2-5 seconds
- With Notion data: +1-2 seconds
- With web search: +2-3 seconds
- Complex queries may take longer

## API Costs

Using OpenAI GPT-4o:
- Text: ~$0.005 per message
- Image analysis: ~$0.01 per image
- Typical monthly cost: $5-20 (depending on usage)

Monitor usage at: https://platform.openai.com/usage

## Security Notes

✅ **Secure:**
- API keys stored in `.env` (not in code)
- File size limits prevent abuse
- No persistent file storage
- Input validation on all uploads

⚠️ **Remember:**
- Don't share your `.env` file
- Don't commit API keys to git
- Review AI responses for accuracy
- Use for educational purposes only

## Next Steps

1. ✅ Install dependencies: `python setup_chat.py`
2. ✅ Add OpenAI API key to `.env`
3. ✅ Start dashboard: `python main.py`
4. ✅ Open chat: `http://localhost:8080/chat`
5. 🎉 Start chatting with Ultron!

## Documentation

- **Full Chat Docs:** `CHAT_SYSTEM_DOCS.md`
- **Development Guide:** `DEVELOPMENT.md`
- **Testing Guide:** `TESTING_GUIDE.md`
- **Project Structure:** `PROJECT_STRUCTURE.md`

## Support

Having issues? Check:
1. Console logs for errors
2. `.env` file is configured correctly
3. All dependencies are installed
4. Internet connection is active

---

**Built with ❤️ for students who want an AI-powered academic assistant!**

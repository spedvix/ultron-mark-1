<p align="center">
  <h1 align="center">U.L.T.R.O.N. Mark I</h1>
  <p align="center">
    <em>Unified Lecture Tracker Reminder & Organizer Network — Prototype</em>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/status-prototype-orange?style=flat-square" alt="Status: Prototype">
    <img src="https://img.shields.io/badge/python-3.9+-blue?style=flat-square&logo=python&logoColor=white" alt="Python 3.9+">
    <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License: MIT">
  </p>
</p>

---

> **⚠️ Prototype Notice:** Ultron Mark I is an early-stage prototype. It is functional but under active development. APIs, data models, and features may change without notice.

## Overview

Ultron is an AI-powered academic assistant designed to help university students manage their academic life. It integrates with university portals, Notion databases, Google Calendar, and Telegram to provide a unified interface for tracking assignments, exams, schedules, and announcements — all powered by an intelligent conversational AI.

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **AI Chat Interface** | Conversational assistant powered by GPT-4o with function-calling, web search, and file analysis |
| 📚 **Notion Integration** | Syncs courses, assignments, and schedules from Notion databases |
| 📅 **Google Calendar** | Reads and manages academic events from Google Calendar |
| 🔔 **Announcement Monitoring** | Automatically scrapes university announcements via Selenium |
| 📱 **Telegram Bot** | Receive reminders, daily schedules, and weekly summaries |
| 📊 **Web Dashboard** | Visual overview of your academic life via FastAPI |
| 🔍 **Web Search** | Real-time information retrieval via DuckDuckGo |
| 🖼️ **File Analysis** | Upload images and PDFs for AI-powered analysis |
| ⏰ **Smart Reminders** | Automated deadline alerts at 7, 3, and 1 day intervals |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACES                       │
│   🌐 Web Chat    📱 Telegram Bot    📊 Dashboard        │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  FASTAPI BACKEND                         │
│          REST API · File Processing · Sessions           │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              ULTRON AGENT (LangGraph)                     │
│   Query Analysis → Tool Selection → Response Generation  │
└───┬──────────┬──────────┬──────────┬────────────────────┘
    │          │          │          │
    ▼          ▼          ▼          ▼
 Notion    Google     Web        OpenAI
  API     Calendar   Search     GPT-4o
```

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **Language** | Python 3.9+ |
| **AI/LLM** | OpenAI GPT-4o, LangChain, LangGraph |
| **Backend** | FastAPI, Uvicorn |
| **Database** | SQLAlchemy, SQLite |
| **Integrations** | Notion API, Google Calendar API, Telegram Bot API |
| **Scraping** | Selenium, BeautifulSoup4 |
| **Scheduling** | APScheduler |
| **Search** | DuckDuckGo Search |

## 📁 Project Structure

```
Ultron_P_MKI/
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
├── alembic.ini              # Database migrations config
│
├── src/                     # Primary source (legacy modules)
│   ├── ai/                  # AI agent & chat handler
│   ├── config/              # Settings & configuration
│   ├── dashboard/           # Web dashboard (FastAPI + Jinja2)
│   ├── database/            # Knowledge base
│   ├── google/              # Google Calendar integration
│   ├── notion/              # Notion API client
│   ├── scheduler/           # Task scheduler & reminders
│   ├── scraper/             # University announcement scraper
│   ├── telegram_bot/        # Telegram bot handlers
│   └── utils/               # Shared utilities
│
├── ultron/                  # Refactored core package
│   ├── api/                 # REST API routes
│   ├── connectors/          # External service connectors
│   ├── db/                  # Database models & migrations
│   ├── extractors/          # Data extraction modules
│   ├── scheduler/           # Async scheduler
│   ├── services/            # Business logic services
│   └── tests/               # Unit & integration tests
│
├── docs/                    # Documentation
│   ├── ARCHITECTURE_DIAGRAM.md
│   ├── CHAT_QUICKSTART.md
│   ├── CHAT_SYSTEM_DOCS.md
│   ├── DEVELOPMENT.md
│   ├── SETUP.md
│   └── ...
│
└── notion_templates/        # Notion import templates
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- An OpenAI API key
- (Optional) Notion integration token
- (Optional) Telegram bot token
- (Optional) Google Calendar credentials

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Ultron_P_MKI.git
cd Ultron_P_MKI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and settings
```

### Running

```bash
python main.py
```

The dashboard will be available at **http://localhost:8080** and the chat interface at **http://localhost:8080/chat**.

## ⚙️ Configuration

Copy `.env.example` to `.env` and configure:

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | ✅ | OpenAI API key for the AI chat system |
| `NOTION_API_KEY` | ❌ | Notion integration token for database sync |
| `TELEGRAM_BOT_TOKEN` | ❌ | Telegram bot token for notifications |
| `GOOGLE_CALENDAR_*` | ❌ | Google Calendar OAuth credentials |
| `UNI_WEBSITE_URL` | ❌ | University website URL for announcement scraping |

See `.env.example` for the full list of configuration options.

## 📖 Documentation

Detailed documentation is available in the [`docs/`](docs/) directory:

- **[Architecture Diagram](docs/ARCHITECTURE_DIAGRAM.md)** — System architecture and data flows
- **[Chat Quickstart](docs/CHAT_QUICKSTART.md)** — Getting started with the AI chat
- **[Setup Guide](docs/SETUP.md)** — Detailed setup instructions
- **[Development Guide](docs/DEVELOPMENT.md)** — Contributing and development workflow
- **[Integration Guide](docs/INTEGRATION_GUIDE.md)** — External service integration details
- **[Testing Guide](docs/TESTING_GUIDE.md)** — Running tests

## 📄 License

This project is licensed under the MIT License.

---

<p align="center">
  <sub>Ultron Mark I — A prototype by a student, for students. 🎓</sub>
</p>

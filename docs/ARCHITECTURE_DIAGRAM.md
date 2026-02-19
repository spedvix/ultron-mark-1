# Ultron AI Chat System - Visual Architecture

## System Overview
```
┌─────────────────────────────────────────────────────────────────────┐
│                         ULTRON AI CHAT SYSTEM                        │
│                     ChatGPT-Style Interface for Students             │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                            USER INTERFACES                           │
├─────────────────────────────────────┬───────────────────────────────┤
│  🌐 Web Chat Interface              │  📱 Telegram Bot (Intact)    │
│  http://localhost:8080/chat         │  Original functionality      │
│                                     │                              │
│  Features:                          │  Features:                   │
│  • Text conversations               │  • All original commands     │
│  • File uploads (images, PDFs)      │  • Notifications            │
│  • Web search                       │  • Reminders                │
│  • Real-time responses              │  • Reports                  │
│  • Modern UI                        │  • Telegram interface       │
└─────────────────────────────────────┴───────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         BACKEND API LAYER                            │
│                          (FastAPI)                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  GET  /chat                  → Render chat interface                │
│  POST /api/chat              → Process chat messages                │
│  POST /api/chat/analyze-image → Dedicated image analysis           │
│                                                                      │
│  Handles:                                                           │
│  • Multipart form data (text + files)                              │
│  • Conversation history management                                 │
│  • File upload processing                                          │
│  • Error handling & validation                                     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FILE PROCESSOR LAYER                            │
│                    (src/ai/file_processor.py)                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  🖼️  Images (JPG, PNG, GIF, etc.)                                   │
│     └─→ Optimize for GPT-4 Vision (max 2048x2048)                  │
│     └─→ Convert to base64 encoding                                 │
│                                                                      │
│  📄  PDFs                                                            │
│     └─→ Extract text from all pages                                │
│     └─→ Maintain pagination info                                   │
│                                                                      │
│  📝  Text Files (TXT, MD, code files)                               │
│     └─→ Detect encoding (UTF-8, Latin-1, etc.)                     │
│     └─→ Syntax-aware processing                                    │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ULTRON AGENT - AI BRAIN                           │
│                  (src/ai/ultron_agent.py)                            │
│                    Built with LangGraph                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│                 ┌─────────────────────────┐                         │
│                 │   1. ANALYZE QUERY      │                         │
│                 │   Determine intent      │                         │
│                 │   and required data     │                         │
│                 └──────────┬──────────────┘                         │
│                            │                                         │
│         ┌──────────────────┼──────────────────┐                     │
│         │                  │                  │                     │
│         ▼                  ▼                  ▼                     │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐               │
│  │ 2a. NOTION  │  │ 2b. WEB      │  │ 2c. DIRECT  │               │
│  │    DATA     │  │    SEARCH    │  │  RESPONSE   │               │
│  │             │  │              │  │             │               │
│  │ Fetch:      │  │ DuckDuckGo   │  │ Simple AI   │               │
│  │ • Assign.   │  │ Search API   │  │ response    │               │
│  │ • Exams     │  │              │  │             │               │
│  │ • Schedule  │  │ Returns web  │  │ No external │               │
│  │ • Classes   │  │ results      │  │ data needed │               │
│  └─────────────┘  └──────────────┘  └─────────────┘               │
│         │                  │                  │                     │
│         └──────────────────┼──────────────────┘                     │
│                            │                                         │
│                            ▼                                         │
│                 ┌─────────────────────────┐                         │
│                 │ 3. GENERATE RESPONSE    │                         │
│                 │                         │                         │
│                 │ GPT-4o processes:       │                         │
│                 │ • User message          │                         │
│                 │ • Conversation history  │                         │
│                 │ • Notion data (if any)  │                         │
│                 │ • Search results        │                         │
│                 │ • File content          │                         │
│                 │                         │                         │
│                 │ Returns contextual      │                         │
│                 │ response with metadata  │                         │
│                 └─────────────────────────┘                         │
└─────────────────────────────────────────────────────────────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            │                   │                   │
            ▼                   ▼                   ▼
┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐
│  OPENAI GPT-4o   │  │  NOTION API      │  │  DUCKDUCKGO     │
│                  │  │                  │  │                 │
│  • Text Gen      │  │  • Assignments   │  │  • Web Search   │
│  • Vision        │  │  • Exams         │  │  • News         │
│  • Reasoning     │  │  • Schedule      │  │  • Current Info │
│  • Context       │  │  • Classes       │  │                 │
└──────────────────┘  └──────────────────┘  └─────────────────┘
```

## Data Flow Example

### Example Query: "How many days until my calculus exam?"

```
Step 1: User Input
┌────────────────────────────────────────────┐
│ User types in chat interface:              │
│ "How many days until my calculus exam?"    │
└────────────────────────────────────────────┘
                    │
                    ▼
Step 2: API Reception
┌────────────────────────────────────────────┐
│ POST /api/chat                             │
│ message: "How many days until my..."       │
│ conversation_history: []                   │
└────────────────────────────────────────────┘
                    │
                    ▼
Step 3: Query Analysis
┌────────────────────────────────────────────┐
│ UltronAgent.analyze_query()                │
│                                            │
│ Keywords detected:                         │
│ • "days" → time calculation needed         │
│ • "exam" → Notion data needed             │
│ • "calculus" → specific exam filter       │
│                                            │
│ Decision: needs_notion_data = True         │
└────────────────────────────────────────────┘
                    │
                    ▼
Step 4: Fetch Notion Data
┌────────────────────────────────────────────┐
│ NotionManager.get_exams()                  │
│                                            │
│ Returns:                                   │
│ [                                          │
│   {                                        │
│     "name": "Calculus Midterm",           │
│     "date": "2025-11-03",                 │
│     "days_left": 12                       │
│   },                                       │
│   {...}, {...}                            │
│ ]                                          │
└────────────────────────────────────────────┘
                    │
                    ▼
Step 5: Generate Response
┌────────────────────────────────────────────┐
│ GPT-4o processes:                          │
│                                            │
│ System: "You are Ultron... [Notion data]"  │
│ User: "How many days until calculus exam?" │
│                                            │
│ AI analyzes data and responds:             │
│ "Your Calculus Midterm is in 12 days,     │
│  scheduled for November 3rd. I recommend   │
│  starting your review this week!"          │
│                                            │
│ Metadata:                                  │
│ • used_notion_data: true                   │
│ • timestamp: 2025-10-22T...               │
└────────────────────────────────────────────┘
                    │
                    ▼
Step 6: Display to User
┌────────────────────────────────────────────┐
│ Chat Interface shows:                      │
│                                            │
│ ┌────────────────────────────────────┐    │
│ │ AI: Your Calculus Midterm is in    │    │
│ │     12 days, scheduled for...       │    │
│ │                                     │    │
│ │ [📊 Notion Data] [🕐 10:30 AM]     │    │
│ └────────────────────────────────────┘    │
└────────────────────────────────────────────┘
```

## State Machine (LangGraph)

```
                    START
                      │
                      ▼
            ┌──────────────────┐
            │  ANALYZE QUERY   │
            │                  │
            │  • Parse message │
            │  • Detect intent │
            │  • Set flags     │
            └────────┬─────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
needs_notion  needs_search   neither
         │           │           │
         ▼           ▼           ▼
  ┌───────────┐ ┌──────────┐ ┌──────────┐
  │  NOTION   │ │   WEB    │ │  DIRECT  │
  │   DATA    │ │  SEARCH  │ │ RESPONSE │
  └─────┬─────┘ └────┬─────┘ └────┬─────┘
        │            │            │
        └────────────┼────────────┘
                     │
                     ▼
            ┌──────────────────┐
            │    GENERATE      │
            │    RESPONSE      │
            │                  │
            │  • Combine data  │
            │  • Create reply  │
            │  • Add metadata  │
            └────────┬─────────┘
                     │
                     ▼
                    END
```

## Conversation Context Flow

```
User Session Timeline:
═════════════════════════════════════════════════════

Message 1:
┌────────────────────────────────────┐
│ U: "What assignments do I have?"   │
│ A: [Lists 5 assignments]           │
│                                    │
│ History: [Msg 1]                   │
└────────────────────────────────────┘

Message 2:
┌────────────────────────────────────┐
│ U: "Which one is due first?"       │
│ A: "Based on the assignments I     │
│     just listed, the Python        │
│     project is due first..."       │
│                                    │
│ History: [Msg 1, Msg 2]            │
└────────────────────────────────────┘
         Uses context from Msg 1!
         
Message 3:
┌────────────────────────────────────┐
│ U: "How long will that take?"      │
│ A: "The Python project typically   │
│     takes 4-6 hours based on..."   │
│                                    │
│ History: [Msg 1, Msg 2, Msg 3]     │
└────────────────────────────────────┘
         Knows "that" = Python project
```

## File Upload Flow

```
┌──────────────────────────────────────────┐
│  User selects file in browser            │
│  (e.g., lecture_notes.pdf)               │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  Frontend preview                        │
│  Shows filename and size                 │
└──────────────┬───────────────────────────┘
               │
               ▼ (User clicks Send)
┌──────────────────────────────────────────┐
│  POST /api/chat                          │
│  Content-Type: multipart/form-data       │
│                                          │
│  Form fields:                            │
│  • message: "Summarize this"            │
│  • file: [binary data]                  │
│  • conversation_history: [...]          │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  FileProcessor.process_file()            │
│                                          │
│  1. Detect file type (.pdf)             │
│  2. Validate size (< 10MB)              │
│  3. Extract text from PDF               │
│  4. Return processed content            │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  UltronAgent.chat()                      │
│                                          │
│  message: "Summarize this"              │
│  file_content: "Lecture notes text..."  │
│                                          │
│  GPT-4o processes both!                 │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│  Response with summary                   │
│  "Here's a summary of the lecture..."    │
└──────────────────────────────────────────┘
```

## Integration Points

```
┌─────────────────────────────────────────────┐
│          EXISTING ULTRON SYSTEMS            │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐    ┌─────────────────┐   │
│  │ Notion       │    │ Telegram Bot    │   │
│  │ Manager      │────│ (Unchanged)     │   │
│  │              │    │                 │   │
│  │ Used by both │    │ Still works!    │   │
│  │ chat & bot   │    └─────────────────┘   │
│  └──────┬───────┘                           │
│         │                                    │
│         │      ┌──────────────────┐         │
│         └──────│  NEW: Chat       │         │
│                │  System          │         │
│                │                  │         │
│                │  • UltronAgent   │         │
│                │  • FileProcessor │         │
│                │  • Chat UI       │         │
│                └──────────────────┘         │
│                                             │
│  Both systems coexist peacefully!          │
└─────────────────────────────────────────────┘
```

## Technology Stack Layers

```
┌─────────────────────────────────────────────┐
│          PRESENTATION LAYER                 │
│  • HTML/CSS/JavaScript                      │
│  • Responsive design                        │
│  • Real-time updates                        │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│          APPLICATION LAYER                  │
│  • FastAPI (REST API)                       │
│  • Form data handling                       │
│  • Session management                       │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│          BUSINESS LOGIC LAYER               │
│  • UltronAgent (LangGraph)                  │
│  • FileProcessor                            │
│  • Query analysis                           │
│  • Response generation                      │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│          AI/ML LAYER                        │
│  • OpenAI GPT-4o                            │
│  • LangChain orchestration                  │
│  • Token management                         │
│  • Prompt engineering                       │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│          DATA LAYER                         │
│  • Notion API                               │
│  • DuckDuckGo Search                        │
│  • File system                              │
│  • Conversation cache                       │
└─────────────────────────────────────────────┘
```

---

**This architecture provides:**
- ✅ Scalability (can add more nodes to LangGraph)
- ✅ Modularity (each component is independent)
- ✅ Maintainability (clear separation of concerns)
- ✅ Extensibility (easy to add new features)
- ✅ Reliability (error handling at each layer)

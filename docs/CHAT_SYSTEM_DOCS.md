# Ultron AI Chat System Documentation

## Overview

The Ultron AI Chat System is a sophisticated conversational AI interface that provides students with an intelligent assistant capable of:
- Understanding and answering questions about their Notion workspace data (assignments, exams, schedules)
- Performing web searches for current information
- Analyzing images using GPT-4 Vision
- Processing uploaded documents (PDFs, text files, code)
- Providing personalized academic advice and insights

## Architecture

### Components

#### 1. **UltronAgent** (`src/ai/ultron_agent.py`)
The core AI agent built with LangGraph, implementing a sophisticated workflow:

**Key Features:**
- **LangGraph Workflow**: Multi-node state machine for intelligent query routing
- **Notion Integration**: Deep integration with student's academic data
- **Web Search**: DuckDuckGo search for current information
- **Multimodal Support**: Handles text, images, and documents
- **Context-Aware**: Maintains conversation history and context

**Workflow Nodes:**
1. `analyze_query` - Determines what resources are needed
2. `fetch_notion_data` - Retrieves relevant academic data
3. `web_search` - Performs internet searches
4. `generate_response` - Creates contextual responses

**State Management:**
```python
class AgentState(TypedDict):
    messages: Sequence[BaseMessage]
    notion_data: Optional[Dict]
    search_results: Optional[List[str]]
    file_contents: Optional[List[Dict]]
    needs_search: bool
    needs_notion_data: bool
    final_response: Optional[str]
```

#### 2. **FileProcessor** (`src/ai/file_processor.py`)
Handles various file types for AI analysis:

**Supported Formats:**
- **Images**: JPG, PNG, GIF, BMP, WebP
- **Documents**: PDF (with text extraction)
- **Text Files**: TXT, MD, PY, JS, Java, C/C++, HTML, CSS

**Features:**
- Automatic image optimization for GPT-4 Vision (max 2048x2048)
- PDF text extraction with pagination
- Text encoding detection (UTF-8, Latin-1, CP1252)
- File size validation (10MB limit)
- Base64 encoding for images

#### 3. **Dashboard Integration** (`src/dashboard/app.py`)
FastAPI endpoints for chat functionality:

**Endpoints:**
- `GET /chat` - Chat interface page
- `POST /api/chat` - Main chat endpoint with multimodal support
- `POST /api/chat/analyze-image` - Dedicated image analysis

**Features:**
- Form data handling for file uploads
- Conversation history management
- Error handling and validation

#### 4. **Chat Interface** (`src/dashboard/templates/chat.html`)
Modern, responsive web interface:

**UI Features:**
- Real-time messaging
- File upload with preview
- Typing indicators
- Metadata badges (Notion data, web search)
- Auto-resizing text input
- Conversation history display
- Mobile-responsive design

## Usage Examples

### Basic Questions
```
User: "How many assignments do I have?"
Ultron: Analyzes Notion data and provides count with details

User: "What classes do I have today?"
Ultron: Checks schedule and lists today's classes

User: "When is my next exam?"
Ultron: Calculates days until exams and provides dates
```

### Complex Queries
```
User: "How many days until my calculus exam?"
Ultron: 
1. Fetches exam data from Notion
2. Identifies calculus exam
3. Calculates days remaining
4. Provides detailed response

User: "Which assignments should I finish this week?"
Ultron:
1. Retrieves all assignments
2. Filters by due date
3. Prioritizes by urgency
4. Suggests completion order
```

### Web Search
```
User: "What's the latest news about AI?"
Ultron:
1. Detects search intent
2. Performs DuckDuckGo search
3. Summarizes results
4. Provides relevant information
```

### Image Analysis
```
User: Uploads image of handwritten notes + "Can you help me understand this?"
Ultron:
1. Processes image
2. Uses GPT-4 Vision to analyze
3. Extracts text/concepts
4. Provides explanation
```

### Document Processing
```
User: Uploads PDF + "Summarize this lecture"
Ultron:
1. Extracts text from PDF
2. Analyzes content
3. Provides structured summary
4. Answers follow-up questions
```

## Technical Details

### LangGraph Workflow

```
Entry Point
    ↓
analyze_query (Determine needs)
    ↓
    ├─→ fetch_notion_data → generate_response → END
    ├─→ web_search → generate_response → END
    └─→ generate_response → END
```

### Decision Logic

**Notion Data Trigger Keywords:**
- assignment, exam, class, schedule, course, deadline
- homework, project, quiz, test, midterm, final
- due date, calendar, today, tomorrow, this week
- "how many", "which", "when is"

**Web Search Trigger Keywords:**
- search, find, look up, what is, who is
- define, explain, current, latest, news

### Data Flow

1. **User Input** → Chat Interface
2. **Form Data** → FastAPI Endpoint
3. **File Processing** → FileProcessor (if file uploaded)
4. **Agent Processing** → UltronAgent
   - Query Analysis
   - Data Fetching (Notion/Web)
   - Response Generation
5. **Response** → User Interface

### Notion Data Structure

The agent provides comprehensive academic metrics:

```json
{
  "assignments": {
    "all": [...],
    "urgent": [...],  // < 3 days
    "upcoming": [...], // < 7 days
    "total": 15
  },
  "exams": {
    "all": [...],
    "total": 3
  },
  "schedule": {...},
  "classes": [...],
  "current_date": "2025-10-22T...",
  "current_day": "Tuesday"
}
```

### Response Metadata

Every response includes metadata:
```json
{
  "message": "Your response...",
  "metadata": {
    "used_notion_data": true,
    "used_search": false,
    "timestamp": "2025-10-22T..."
  }
}
```

## Installation & Setup

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Environment Variables
Add to `.env`:
```env
OPENAI_API_KEY=your_openai_api_key
NOTION_API_KEY=your_notion_key
NOTION_DATABASE_ID=your_database_id
NOTION_CALENDAR_ID=your_calendar_id
```

### 3. Run Dashboard
```powershell
python main.py
```

### 4. Access Chat
Navigate to: `http://localhost:8080/chat`

## API Reference

### POST /api/chat

**Request:**
```
Content-Type: multipart/form-data

Fields:
- message (required): User's text message
- conversation_history (optional): JSON array of previous messages
- file (optional): Uploaded file
```

**Response:**
```json
{
  "message": "AI response text",
  "metadata": {
    "used_notion_data": true,
    "used_search": false,
    "timestamp": "2025-10-22T..."
  }
}
```

### POST /api/chat/analyze-image

**Request:**
```
Content-Type: multipart/form-data

Fields:
- file (required): Image file
- query (optional): Question about image
```

**Response:**
```json
{
  "analysis": "Image analysis result"
}
```

## Advanced Features

### Conversation Memory
- Maintains last 10 messages for context
- Uses conversation history for coherent responses
- Supports multi-turn conversations

### Intelligent Query Routing
- Automatic detection of query type
- Parallel data fetching when needed
- Optimized response generation

### File Upload Capabilities
- Drag-and-drop support
- Preview before sending
- Multiple format support
- Automatic processing

### Error Handling
- Graceful degradation
- User-friendly error messages
- Automatic retry logic
- Fallback responses

## Best Practices

### For Users

1. **Be Specific**: "When is my calculus exam?" vs "Tell me about exams"
2. **Use Context**: Follow-up questions work better with conversation history
3. **File Uploads**: Ensure files are clear and readable
4. **Complex Queries**: Break down into smaller questions if needed

### For Developers

1. **Token Management**: Monitor OpenAI API usage
2. **Error Logging**: Check logs for debugging
3. **Performance**: Consider caching for frequent queries
4. **Security**: Validate all file uploads
5. **Scalability**: Consider rate limiting for production

## Future Enhancements

Potential improvements:
- [ ] Voice input/output
- [ ] More file format support (Word, Excel)
- [ ] Advanced analytics on academic performance
- [ ] Integration with more data sources
- [ ] Custom study plan generation
- [ ] Collaboration features
- [ ] Mobile app
- [ ] Offline mode

## Troubleshooting

### Common Issues

**Issue: "OpenAI API Error"**
- Check API key in `.env`
- Verify API quota
- Check internet connection

**Issue: "Notion data not loading"**
- Verify Notion API key
- Check database/calendar IDs
- Ensure proper permissions

**Issue: "File upload fails"**
- Check file size (< 10MB)
- Verify file format
- Check file permissions

**Issue: "Web search not working"**
- Check internet connection
- DuckDuckGo availability
- Rate limiting

## Performance Considerations

- **Average Response Time**: 2-5 seconds
- **With Notion Data**: +1-2 seconds
- **With Web Search**: +2-3 seconds
- **With Image Analysis**: +3-5 seconds
- **With PDF Processing**: +2-4 seconds

## Security

- File size limits prevent DOS attacks
- Input validation on all endpoints
- No persistent file storage
- Secure API key management
- CORS protection
- Rate limiting recommended for production

## Credits

Built with:
- OpenAI GPT-4o (text + vision)
- LangChain & LangGraph
- FastAPI
- Notion API
- DuckDuckGo Search

---

**Note**: This is a powerful AI system with access to your personal academic data. Always review responses and use your judgment for important decisions.

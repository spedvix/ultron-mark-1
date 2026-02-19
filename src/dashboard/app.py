"""
FastAPI web dashboard for Ultron
"""
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional, List
import json

from src.notion.notion_manager import NotionManager
from src.google.calendar_manager import GoogleCalendarManager
from src.scraper.announcement_scraper import AnnouncementScraper
from src.ai.ultron_agent import UltronAgent
from src.ai.file_processor import FileProcessor


# Setup paths
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Ensure directories exist
TEMPLATES_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="Ultron Dashboard",
        description="AI Academic Assistant Dashboard",
        version="1.0.0"
    )
    
    # Mount static files
    # app.add_middleware(StaticFiles, directory=str(STATIC_DIR), name="static")
    
    notion = NotionManager()
    calendar = GoogleCalendarManager()
    ultron_agent = UltronAgent()
    
    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request):
        """Dashboard home page"""
        try:
            # Fetch all data
            assignments = calendar.get_assignments() if calendar.client else notion.get_assignments()
            exams = calendar.get_exams() if calendar.client else notion.get_exams()
            schedule = calendar.get_weekly_events() if calendar.client else notion.get_weekly_schedule()
            notion_weekly_classes = notion.get_weekly_schedule()
            
            # Get today's classes
            from datetime import datetime
            today = datetime.now().strftime("%A")
            today_classes = schedule.get(today, [])
            
            # Calculate stats
            total_assignments = len(assignments)
            upcoming_exams = len(exams)
            
            context = {
                "request": request,
                "assignments": assignments[:5],  # Show top 5
                "exams": exams[:3],  # Show top 3
                "today_classes": today_classes,
                "schedule": schedule,
                "total_assignments": total_assignments,
                "upcoming_exams": upcoming_exams,
                "current_date": datetime.now().strftime("%B %d, %Y"),
                "current_day": today,
                "notion_weekly_schedule": notion_weekly_classes,
            }
            
            return templates.TemplateResponse("index.html", context)
            
        except Exception as e:
            return templates.TemplateResponse(
                "error.html",
                {"request": request, "error": str(e)}
            )
    
    @app.get("/api/assignments")
    async def get_assignments():
        """API endpoint for assignments"""
        data = calendar.get_assignments() if calendar.client else notion.get_assignments()
        return {"assignments": data}
    
    @app.get("/api/exams")
    async def get_exams():
        """API endpoint for exams"""
        data = calendar.get_exams() if calendar.client else notion.get_exams()
        return {"exams": data}
    
    @app.get("/api/schedule")
    async def get_schedule():
        """API endpoint for schedule"""
        if calendar.client:
            return {"schedule": calendar.get_weekly_events()}
        return {"schedule": notion.get_weekly_schedule()}

    @app.get("/api/weekly-classes")
    async def get_weekly_classes():
        """API endpoint for Notion-based weekly class schedule"""
        return {"schedule": notion.get_weekly_schedule()}
    
    @app.get("/api/announcements")
    async def get_announcements():
        """API endpoint for announcements"""
        scraper = AnnouncementScraper()
        announcements = scraper.scrape()
        return {"announcements": announcements}
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "Ultron Dashboard"}
    
    @app.get("/chat", response_class=HTMLResponse)
    async def chat_page(request: Request):
        """Chat interface page"""
        return templates.TemplateResponse("chat.html", {"request": request})
    
    @app.post("/api/chat")
    async def chat_endpoint(
        message: str = Form(...),
        conversation_history: Optional[str] = Form(None),
        file: Optional[UploadFile] = File(None)
    ):
        """
        Chat endpoint with multimodal support
        
        Accepts:
        - message: User's text message
        - conversation_history: JSON string of previous messages
        - file: Optional file upload (image, PDF, text, etc.)
        """
        try:
            # Parse conversation history
            history = []
            if conversation_history:
                try:
                    history = json.loads(conversation_history)
                except json.JSONDecodeError:
                    pass
            
            # Process uploaded file if present
            file_content = None
            image_data = None
            
            if file:
                file_bytes = await file.read()
                processed_file = FileProcessor.process_file(file_bytes, file.filename)
                
                if not processed_file.get("success", False):
                    return JSONResponse(
                        status_code=400,
                        content={"error": processed_file.get("error", "File processing failed")}
                    )
                
                # Check file type
                if processed_file["type"] == "image":
                    image_data = processed_file["base64_data"]
                else:
                    file_content = processed_file["content"]
            
            # Get response from Ultron agent
            response = await ultron_agent.chat(
                message=message,
                conversation_history=history,
                image_data=image_data,
                file_content=file_content
            )
            
            return JSONResponse(content=response)
            
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": str(e)}
            )
    
    @app.post("/api/chat/analyze-image")
    async def analyze_image_endpoint(
        file: UploadFile = File(...),
        query: Optional[str] = Form("What's in this image?")
    ):
        """Analyze an uploaded image"""
        try:
            file_bytes = await file.read()
            processed_file = FileProcessor.process_file(file_bytes, file.filename)
            
            if not processed_file.get("success", False):
                return JSONResponse(
                    status_code=400,
                    content={"error": processed_file.get("error", "File processing failed")}
                )
            
            if processed_file["type"] != "image":
                return JSONResponse(
                    status_code=400,
                    content={"error": "File must be an image"}
                )
            
            result = await ultron_agent.analyze_image(
                processed_file["base64_data"],
                query
            )
            
            return JSONResponse(content={"analysis": result})
            
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": str(e)}
            )
    
    return app


# For development
if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8080)

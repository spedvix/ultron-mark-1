"""
Mock Dashboard Test - Test without Notion credentials
This creates a standalone dashboard with sample data
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta

print("=" * 70)
print("⚡ ULTRON NEURAL INTERFACE - DIAGNOSTIC MODE ⚡")
print("=" * 70)
print()

# Setup paths
BASE_DIR = Path(__file__).parent / "src" / "dashboard"
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Create FastAPI app
app = FastAPI(title="Ultron Dashboard Test")

# Mock data
def get_mock_data():
    today = datetime.now()
    
    mock_assignments = [
        {
            "title": "Data Structures Project",
            "class": "CS 201",
            "due_date": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
            "status": "In Progress",
            "priority": "High",
            "description": "Implement a binary search tree with full documentation"
        },
        {
            "title": "Machine Learning Assignment",
            "class": "CS 405",
            "due_date": (today + timedelta(days=7)).strftime("%Y-%m-%d"),
            "status": "Not Started",
            "priority": "Medium",
            "description": "Train a neural network on the MNIST dataset"
        },
        {
            "title": "Database Design Report",
            "class": "CS 301",
            "due_date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
            "status": "In Progress",
            "priority": "High",
            "description": "Design and document a relational database schema"
        }
    ]
    
    mock_exams = [
        {
            "title": "Midterm Exam",
            "class": "CS 201 - Data Structures",
            "date": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
            "type": "Midterm",
            "location": "Room 301"
        },
        {
            "title": "Final Exam",
            "class": "CS 405 - Machine Learning",
            "date": (today + timedelta(days=30)).strftime("%Y-%m-%d"),
            "type": "Final",
            "location": "Room 205"
        }
    ]
    
    mock_today_classes = [
        {
            "name": "Data Structures",
            "instructor": "Dr. Smith",
            "schedule": "10:00-11:30",
            "room": "Room 301"
        },
        {
            "name": "Machine Learning",
            "instructor": "Prof. Johnson",
            "schedule": "14:00-15:30",
            "room": "Room 205"
        }
    ]
    
    mock_schedule = {
        "Monday": [
            {"name": "Data Structures", "instructor": "Dr. Smith", "schedule": "Monday 10:00-11:30", "room": "Room 301"},
            {"name": "Database Systems", "instructor": "Dr. Williams", "schedule": "Monday 14:00-15:30", "room": "Room 102"}
        ],
        "Tuesday": [
            {"name": "Machine Learning", "instructor": "Prof. Johnson", "schedule": "Tuesday 10:00-11:30", "room": "Room 205"}
        ],
        "Wednesday": [
            {"name": "Data Structures", "instructor": "Dr. Smith", "schedule": "Wednesday 10:00-11:30", "room": "Room 301"},
            {"name": "Software Engineering", "instructor": "Dr. Brown", "schedule": "Wednesday 14:00-15:30", "room": "Room 401"}
        ],
        "Thursday": [
            {"name": "Machine Learning", "instructor": "Prof. Johnson", "schedule": "Thursday 10:00-11:30", "room": "Room 205"}
        ],
        "Friday": [
            {"name": "Database Systems", "instructor": "Dr. Williams", "schedule": "Friday 10:00-11:30", "room": "Room 102"}
        ],
        "Saturday": [],
        "Sunday": []
    }
    
    return {
        "assignments": mock_assignments,
        "exams": mock_exams,
        "today_classes": mock_today_classes,
        "schedule": mock_schedule,
        "total_assignments": len(mock_assignments),
        "upcoming_exams": len(mock_exams),
        "current_date": today.strftime("%B %d, %Y"),
        "current_day": today.strftime("%A")
    }

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Mock dashboard home page"""
    context = {"request": request, **get_mock_data()}
    return templates.TemplateResponse("index.html", context)

@app.get("/api/assignments")
async def get_assignments():
    """API endpoint for assignments"""
    return {"assignments": get_mock_data()["assignments"]}

@app.get("/api/exams")
async def get_exams():
    """API endpoint for exams"""
    return {"exams": get_mock_data()["exams"]}

@app.get("/api/schedule")
async def get_schedule():
    """API endpoint for schedule"""
    return {"schedule": get_mock_data()["schedule"]}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Ultron Mock Dashboard",
        "mode": "testing",
        "message": "Using mock data - no credentials required"
    }

# Start the server
if __name__ == "__main__":
    print("✅ NEURAL INTERFACE INITIALIZED")
    print()
    print("⚡ SYSTEM CAPABILITIES:")
    print("   ▶ Mock mission data loaded")
    print("   ▶ No authentication required")
    print("   ▶ Full UI/UX demonstration")
    print()
    print("🌐 NEURAL INTERFACE ACCESS POINTS:")
    print("   ▶ http://localhost:8080")
    print("   ▶ http://127.0.0.1:8080")
    print()
    print("� AVAILABLE PROTOCOLS:")
    print("   ▶ GET  /              - Main Neural Interface")
    print("   ▶ GET  /api/assignments - Mission Data Stream")
    print("   ▶ GET  /api/exams       - Critical Event Data")
    print("   ▶ GET  /api/schedule    - Protocol Timeline")
    print("   ▶ GET  /health          - System Diagnostics")
    print()
    print("⚠️  TERMINATION COMMAND: Ctrl+C")
    print("=" * 70)
    print()
    print("▸ Launching Strategic Interface...")
    print()
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)

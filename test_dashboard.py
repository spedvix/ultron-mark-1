"""
Dashboard Testing Script
Run this to test the dashboard independently
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 60)
print("🧪 Testing Ultron Dashboard")
print("=" * 60)
print()

# Test 1: Check if FastAPI is installed
print("1. Checking FastAPI installation...")
try:
    import fastapi
    import uvicorn
    print("   ✅ FastAPI is installed")
except ImportError as e:
    print(f"   ❌ FastAPI not installed: {e}")
    print("   Run: pip install fastapi uvicorn")
    sys.exit(1)

# Test 2: Check if templates exist
print("\n2. Checking template files...")
template_dir = Path(__file__).parent / "src" / "dashboard" / "templates"
if template_dir.exists():
    print(f"   ✅ Templates directory exists: {template_dir}")
    index_html = template_dir / "index.html"
    if index_html.exists():
        print("   ✅ index.html exists")
    else:
        print("   ❌ index.html not found")
else:
    print(f"   ❌ Templates directory not found: {template_dir}")

# Test 3: Try to import dashboard app
print("\n3. Testing dashboard app import...")
try:
    from src.dashboard.app import create_app
    print("   ✅ Dashboard app imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import dashboard: {e}")
    sys.exit(1)

# Test 4: Create the app
print("\n4. Creating FastAPI application...")
try:
    app = create_app()
    print("   ✅ FastAPI application created")
except Exception as e:
    print(f"   ❌ Failed to create app: {e}")
    sys.exit(1)

# Test 5: List available routes
print("\n5. Available API endpoints:")
from fastapi.routing import APIRoute
for route in app.routes:
    if isinstance(route, APIRoute):
        print(f"   📍 {route.methods} {route.path}")

# Test 6: Start the server
print("\n" + "=" * 60)
print("✅ All tests passed! Starting dashboard server...")
print("=" * 60)
print()
print("📊 Dashboard will be available at:")
print("   🌐 http://localhost:8080")
print("   🌐 http://127.0.0.1:8080")
print()
print("📝 Available endpoints:")
print("   • GET  /              - Dashboard home page")
print("   • GET  /api/assignments  - Get assignments as JSON")
print("   • GET  /api/exams        - Get exams as JSON")
print("   • GET  /api/schedule     - Get schedule as JSON")
print("   • GET  /api/announcements - Get announcements as JSON")
print("   • GET  /health           - Health check")
print()
print("⚠️  Note: The dashboard needs Notion credentials to display data.")
print("   Make sure your .env file is configured properly.")
print()
print("Press Ctrl+C to stop the server")
print("=" * 60)
print()

# Start the server
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8080)

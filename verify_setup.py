"""
Quick verification script to check if Ultron AI Chat System is ready
"""
import sys

def check_imports():
    """Check if all critical packages are installed"""
    required_packages = {
        'openai': 'OpenAI',
        'langchain': 'LangChain',
        'langchain_openai': 'LangChain OpenAI',
        'langgraph': 'LangGraph',
        'fastapi': 'FastAPI',
        'notion_client': 'Notion Client',
        'PIL': 'Pillow',
        'pypdf': 'PyPDF',
    }
    
    missing = []
    installed = []
    
    for package, name in required_packages.items():
        try:
            __import__(package)
            installed.append(name)
        except ImportError:
            missing.append(name)
    
    print("="*60)
    print("ULTRON AI CHAT SYSTEM - PACKAGE CHECK")
    print("="*60)
    
    if installed:
        print("\n✅ Installed packages:")
        for name in installed:
            print(f"  • {name}")
    
    if missing:
        print("\n❌ Missing packages:")
        for name in missing:
            print(f"  • {name}")
        print("\nPlease run: python setup_chat.py")
        return False
    else:
        print("\n🎉 All required packages are installed!")
        print("\nNext steps:")
        print("1. Add OPENAI_API_KEY to .env file")
        print("2. Run: python main.py")
        print("3. Visit: http://localhost:8080/chat")
        return True

if __name__ == "__main__":
    success = check_imports()
    sys.exit(0 if success else 1)

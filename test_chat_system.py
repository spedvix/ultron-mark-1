"""
Test script for Ultron AI Chat System
Run this to verify the chat system is working correctly
"""
import asyncio
from loguru import logger
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ai.ultron_agent import UltronAgent
from src.ai.file_processor import FileProcessor


async def test_basic_chat():
    """Test basic chat functionality"""
    logger.info("Testing basic chat...")
    
    agent = UltronAgent()
    response = await agent.chat("Hello, Ultron! Can you introduce yourself?")
    
    logger.info(f"Response: {response['message'][:100]}...")
    logger.success("✓ Basic chat works!")
    return True


async def test_notion_query():
    """Test Notion data integration"""
    logger.info("Testing Notion data query...")
    
    try:
        agent = UltronAgent()
        response = await agent.chat("How many assignments do I have?")
        
        if response['metadata'].get('used_notion_data'):
            logger.success("✓ Notion integration works!")
            logger.info(f"Response: {response['message'][:100]}...")
            return True
        else:
            logger.warning("⚠ Notion data not used (check if Notion is configured)")
            return False
    except Exception as e:
        logger.error(f"✗ Notion query failed: {e}")
        return False


async def test_conversation_context():
    """Test conversation history"""
    logger.info("Testing conversation context...")
    
    agent = UltronAgent()
    
    # First message
    response1 = await agent.chat("My favorite subject is physics")
    history = [
        {"role": "user", "content": "My favorite subject is physics"},
        {"role": "assistant", "content": response1['message']}
    ]
    
    # Follow-up message
    response2 = await agent.chat(
        "What subject did I just mention?",
        conversation_history=history
    )
    
    if "physics" in response2['message'].lower():
        logger.success("✓ Conversation context works!")
        return True
    else:
        logger.warning("⚠ Context not maintained properly")
        return False


def test_file_processor():
    """Test file processing capabilities"""
    logger.info("Testing file processor...")
    
    # Test with a simple text file
    test_content = "This is a test file for Ultron AI Chat System."
    file_data = test_content.encode('utf-8')
    
    result = FileProcessor.process_file(file_data, "test.txt")
    
    if result.get('success') and result.get('content') == test_content:
        logger.success("✓ File processor works!")
        return True
    else:
        logger.error("✗ File processor failed")
        return False


async def test_web_search():
    """Test web search functionality"""
    logger.info("Testing web search...")
    
    try:
        agent = UltronAgent()
        response = await agent.chat("What's the latest news about artificial intelligence?")
        
        if response['metadata'].get('used_search'):
            logger.success("✓ Web search works!")
            logger.info(f"Response: {response['message'][:100]}...")
            return True
        else:
            logger.warning("⚠ Web search not triggered")
            return False
    except Exception as e:
        logger.error(f"✗ Web search failed: {e}")
        return False


async def main():
    """Run all tests"""
    logger.info("="*60)
    logger.info("ULTRON AI CHAT SYSTEM - TEST SUITE")
    logger.info("="*60)
    
    tests = [
        ("Basic Chat", test_basic_chat),
        ("File Processor", test_file_processor),
        ("Conversation Context", test_conversation_context),
        ("Notion Data Query", test_notion_query),
        ("Web Search", test_web_search),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'─'*60}")
        logger.info(f"Test: {test_name}")
        logger.info(f"{'─'*60}")
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"✗ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status} - {test_name}")
    
    logger.info(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        logger.success("\n🎉 All tests passed! Chat system is ready to use!")
    elif passed > 0:
        logger.warning(f"\n⚠ Some tests failed. Check configuration and dependencies.")
    else:
        logger.error("\n❌ All tests failed. Please check setup and configuration.")
    
    logger.info("\nNext steps:")
    logger.info("1. Ensure .env file has OPENAI_API_KEY")
    logger.info("2. Ensure .env file has NOTION_API_KEY (for Notion tests)")
    logger.info("3. Run: python main.py")
    logger.info("4. Visit: http://localhost:8080/chat")


if __name__ == "__main__":
    asyncio.run(main())

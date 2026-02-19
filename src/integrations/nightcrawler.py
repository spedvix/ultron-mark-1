"""
NightCrawler integration for deep research
"""
import aiohttp
from loguru import logger
from typing import Dict, Optional

from src.config.settings import settings


class NightCrawlerClient:
    """Client for NightCrawler research assistant"""
    
    def __init__(self):
        self.api_url = settings.NIGHTCRAWLER_API_URL
        self.api_key = settings.NIGHTCRAWLER_API_KEY
        
    async def research(self, query: str, research_type: str = "general") -> Dict:
        """
        Perform deep research using NightCrawler
        
        Args:
            query: Research query
            research_type: Type of research (general, academic, technical, etc.)
            
        Returns:
            Research results
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "query": query,
                    "research_type": research_type,
                    "depth": "comprehensive"
                }
                
                async with session.post(
                    f"{self.api_url}/research",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Research completed for: {query}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"NightCrawler API error: {error_text}")
                        return {"error": error_text}
                        
        except Exception as e:
            logger.error(f"Error communicating with NightCrawler: {e}")
            return {"error": str(e)}
    
    async def get_research_status(self, research_id: str) -> Dict:
        """
        Get status of ongoing research
        
        Args:
            research_id: Research task ID
            
        Returns:
            Research status
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                
                async with session.get(
                    f"{self.api_url}/research/{research_id}",
                    headers=headers
                ) as response:
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"Error getting research status: {e}")
            return {"error": str(e)}
    
    async def summarize_research(self, content: str) -> str:
        """
        Get a summary of research content
        
        Args:
            content: Research content to summarize
            
        Returns:
            Summary text
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {"content": content}
                
                async with session.post(
                    f"{self.api_url}/summarize",
                    json=payload,
                    headers=headers
                ) as response:
                    result = await response.json()
                    return result.get("summary", "")
                    
        except Exception as e:
            logger.error(f"Error summarizing research: {e}")
            return f"Error: {str(e)}"


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_nightcrawler():
        client = NightCrawlerClient()
        
        # Perform research
        result = await client.research(
            query="Machine learning algorithms for classification",
            research_type="academic"
        )
        
        print("Research Result:", result)
    
    asyncio.run(test_nightcrawler())

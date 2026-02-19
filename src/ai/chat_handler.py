"""
AI Chat Handler for Ultron - manages conversations and consultancy
"""
from openai import AsyncOpenAI
from loguru import logger
from typing import List, Dict, Optional
import json

from src.config.settings import settings


class ChatHandler:
    """Handles AI-powered chat and consultancy"""
    
    def __init__(self):
        self.model_name = settings.OPENAI_CHAT_MODEL or "gpt-5-mini"
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.conversation_history: List[Dict] = []
        self.system_prompt = """You are Ultron, an AI academic assistant designed to help students manage their academic life.

Your capabilities include:
- Providing study strategies and academic advice
- Helping with time management and organization
- Answering questions about courses and assignments
- Offering motivational support
- Creating study plans tailored to individual needs

Be helpful, encouraging, and professional. Always provide actionable advice when possible."""
        
        # Initialize conversation
        self.conversation_history.append({
            "role": "system",
            "content": self.system_prompt
        })
    
    async def get_response(self, user_message: str, context: Optional[Dict] = None) -> str:
        """
        Get AI response to user message
        
        Args:
            user_message: The user's message
            context: Optional context (assignments, schedule, etc.)
            
        Returns:
            AI response
        """
        try:
            # Add context if provided
            if context:
                context_message = f"\n\nContext: {json.dumps(context, indent=2)}"
                user_message += context_message
            
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Get response from OpenAI
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=self.conversation_history,
                temperature=0.7,
                max_completion_tokens=1000
            )
            
            assistant_message = response.choices[0].message.content
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            # Keep conversation history manageable (last 20 messages)
            if len(self.conversation_history) > 20:
                # Keep system prompt and last 19 messages
                self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-19:]
            
            return assistant_message
            
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return "I apologize, but I encountered an error processing your request. Please try again."
    
    async def get_study_strategy(self, subject: str, time_available: str, difficulty: str) -> str:
        """
        Generate a personalized study strategy
        
        Args:
            subject: The subject to study
            time_available: How much time is available (e.g., "2 weeks", "3 days")
            difficulty: Current difficulty level ("easy", "medium", "hard")
            
        Returns:
            Study strategy recommendations
        """
        prompt = f"""Create a detailed study strategy for the following:

Subject: {subject}
Time Available: {time_available}
Current Difficulty Level: {difficulty}

Please provide:
1. A day-by-day study plan
2. Recommended study techniques for this subject
3. Time allocation suggestions
4. Tips for retention and understanding
5. Practice/review recommendations"""

        return await self.get_response(prompt)
    
    async def analyze_academic_performance(self, grades: List[Dict], current_gpa: float) -> str:
        """
        Analyze academic performance and provide recommendations
        
        Args:
            grades: List of recent grades
            current_gpa: Current GPA
            
        Returns:
            Performance analysis and recommendations
        """
        grades_str = json.dumps(grades, indent=2)
        
        prompt = f"""Analyze my academic performance and provide recommendations:

Current GPA: {current_gpa}

Recent Grades:
{grades_str}

Please provide:
1. Analysis of current performance
2. Subjects that need more attention
3. Strategies to improve GPA
4. Motivation and encouragement"""

        return await self.get_response(prompt)
    
    async def get_assignment_help(self, assignment: Dict) -> str:
        """
        Get help with an assignment
        
        Args:
            assignment: Assignment details
            
        Returns:
            Helpful suggestions and approach
        """
        prompt = f"""I need help with this assignment:

Title: {assignment.get('title')}
Class: {assignment.get('class')}
Due Date: {assignment.get('due_date')}
Description: {assignment.get('description')}

Please provide:
1. How to approach this assignment
2. Time management suggestions
3. Key points to focus on
4. Resources that might help"""

        return await self.get_response(prompt)
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ]
        logger.info("Conversation history reset")
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation"""
        messages = [msg["content"] for msg in self.conversation_history if msg["role"] != "system"]
        return "\n\n".join(messages[-5:])  # Last 5 messages


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_chat():
        handler = ChatHandler()
        
        # Test basic chat
        response = await handler.get_response("How can I improve my study habits?")
        print(f"Response: {response}\n")
        
        # Test study strategy
        strategy = await handler.get_study_strategy(
            subject="Data Structures",
            time_available="2 weeks",
            difficulty="medium"
        )
        print(f"Study Strategy: {strategy}\n")
    
    asyncio.run(test_chat())

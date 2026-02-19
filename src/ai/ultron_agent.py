"""
Advanced Ultron AI agent powered by OpenAI function-calling.
Routes user requests to data sources (Notion, Google Calendar, announcements, web search)
without relying on keyword heuristics.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolExecutor, ToolInvocation

from loguru import logger

from langchain_community.tools import DuckDuckGoSearchResults

from src.config.settings import settings
from src.database.knowledge_base import KnowledgeBase
from src.google.calendar_manager import GoogleCalendarManager
from src.notion.notion_manager import NotionManager
from src.scraper.announcement_scraper import AnnouncementScraper


class UltronAgent:
    """Multi-modal assistant orchestrated through OpenAI tool-calling."""

    def __init__(self) -> None:
        self.notion_manager = NotionManager()
        self.calendar_manager = GoogleCalendarManager()
        self.announcement_scraper = AnnouncementScraper()
        self.search_tool = DuckDuckGoSearchResults(num_results=5, backend="news")
        self.knowledge_base = KnowledgeBase()

        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY,
        )

        self.tools = self._build_tools()
        self.tool_executor = ToolExecutor(self.tools)
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    # ------------------------------------------------------------------ #
    # Tool definitions
    # ------------------------------------------------------------------ #
    def _build_tools(self) -> List[StructuredTool]:
        return [
            StructuredTool.from_function(
                func=self._tool_fetch_assignments,
                name="fetch_assignments",
                description="Fetch upcoming assignments/tasks for the student.",
            ),
            StructuredTool.from_function(
                func=self._tool_fetch_exams,
                name="fetch_exams",
                description="Fetch upcoming exams and assessments.",
            ),
            StructuredTool.from_function(
                func=self._tool_fetch_schedule,
                name="fetch_weekly_schedule",
                description="Fetch the class schedule. Optionally specify a day name (e.g. 'Monday').",
            ),
            StructuredTool.from_function(
                func=self._tool_fetch_courses,
                name="fetch_courses",
                description="Fetch course metadata from Notion.",
            ),
            StructuredTool.from_function(
                func=self._tool_fetch_announcements,
                name="fetch_announcements",
                description="Fetch recent university announcements (defaults to latest five).",
            ),
            StructuredTool.from_function(
                func=self._tool_search_notion_notes,
                name="search_notion_notes",
                description="Search Notion for notes. Provide a query and optionally course_name or limit for targeted results.",
            ),
            StructuredTool.from_function(
                func=self._tool_search_course_materials,
                name="search_course_materials",
                description="Search stored course materials (chapters, notes, summaries). Provide a query and optionally course_code, chapter, or limit.",
            ),
            StructuredTool.from_function(
                func=self._tool_get_course_material,
                name="get_course_material",
                description="Retrieve the full details of a stored course material by material_id.",
            ),
            StructuredTool.from_function(
                func=self._tool_list_material_courses,
                name="list_material_courses",
                description="List course codes that have stored materials in the internal database.",
            ),
            StructuredTool.from_function(
                func=self._tool_web_search,
                name="web_search",
                description="Perform a web search for up-to-date information.",
            ),
            StructuredTool.from_function(
                func=self._tool_fetch_logs,
                name="fetch_logs",
                description="Fetch Ultron system logs for health/status checks. Optional parameters: hours (default 24), max_lines (default 1000).",
            ),
        ]

    def _tool_fetch_assignments(self, days: int = 14) -> str:
        data = self.calendar_manager.get_assignments() if self.calendar_manager.client else self.notion_manager.get_assignments()
        if days and isinstance(days, int):
            data = self._filter_by_days(data, key="due_date", days=days)
        return self._to_json(data)

    def _tool_fetch_exams(self, days: int = 60) -> str:
        data = self.calendar_manager.get_exams() if self.calendar_manager.client else self.notion_manager.get_exams()
        if days and isinstance(days, int):
            data = self._filter_by_days(data, key="date", days=days)
        return self._to_json(data)

    def _tool_fetch_schedule(self, day: Optional[str] = None) -> str:
        schedule = self.calendar_manager.get_weekly_events() if self.calendar_manager.client else self.notion_manager.get_weekly_schedule()
        if day:
            day_title = day.strip().title()
            schedule = {day_title: schedule.get(day_title, [])}
        return self._to_json(schedule)

    def _tool_fetch_courses(self) -> str:
        courses = self.notion_manager.get_courses()
        return self._to_json(courses)

    def _tool_fetch_announcements(self, limit: int = 5) -> str:
        announcements = self.announcement_scraper.scrape()
        if isinstance(limit, int) and limit > 0:
            announcements = announcements[:limit]
        return self._to_json(announcements)

    def _tool_search_notion_notes(
        self,
        query: str = "",
        course_name: Optional[str] = None,
        limit: int = 5,
    ) -> str:
        query = (query or "").strip()
        if not query:
            return self._to_json({"error": "query is required"})
        notes = self.notion_manager.search_notes(query=query, course_name=course_name, limit=limit)
        payload = {
            "query": query,
            "course_name": course_name,
            "count": len(notes),
            "notes": notes,
        }
        if not notes:
            payload["message"] = "No matching Notion pages were found."
        else:
            summary_lines = []
            for idx, item in enumerate(notes, start=1):
                summary_lines.append(
                    f"{idx}. {item['title']} ({item.get('course') or 'Course not tagged'}) -> {item.get('url')}"
                )
            payload["summary"] = "\n".join(summary_lines)
        return self._to_json(payload)

    def _tool_search_course_materials(
        self,
        query: str = "",
        course_code: Optional[str] = None,
        chapter: Optional[str] = None,
        limit: int = 5,
    ) -> str:
        if not any([query, course_code, chapter]):
            return self._to_json({"error": "Provide at least a query, course_code, or chapter to search."})
        results = self.knowledge_base.search_materials(
            query=query or None,
            course_code=course_code,
            chapter=chapter,
            limit=limit,
        )
        return self._to_json(results)

    def _tool_get_course_material(self, material_id: int) -> str:
        material = self.knowledge_base.get_material(material_id)
        if not material:
            return self._to_json({"error": f"Material with id {material_id} was not found."})
        return self._to_json(material)

    def _tool_list_material_courses(self) -> str:
        courses = self.knowledge_base.list_courses()
        return self._to_json({"courses": courses})

    def _tool_web_search(self, query: str, num_results: int = 5) -> str:
        if not query:
            return "[]"
        original_num = self.search_tool.num_results
        self.search_tool.num_results = max(1, min(num_results, 10))
        try:
            results = self.search_tool.run(query)
        finally:
            self.search_tool.num_results = original_num
        return self._to_json(results if isinstance(results, list) else [results])

    def _tool_fetch_logs(self, hours: int = 24, max_lines: int = 1000) -> str:
        log_path = settings.LOGS_DIR / settings.LOG_FILE_NAME
        if not log_path.exists():
            return self._to_json({"error": f"log file not found at {log_path}"})

        try:
            cutoff = datetime.now() - timedelta(hours=max(1, hours))
            lines: List[str] = []
            with log_path.open("r", encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    parts = line.split(" | ", 1)
                    if not parts:
                        continue
                    try:
                        timestamp = datetime.strptime(parts[0].strip(), "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        continue
                    if timestamp >= cutoff:
                        lines.append(line.rstrip())
            if not lines:
                return self._to_json({"message": "No log entries within requested window."})
            return self._to_json({"log_path": str(log_path), "entries": lines[-max(10, min(max_lines, len(lines))):]})
        except Exception as exc:
            return self._to_json({"error": f"failed to read logs: {exc}"})

    # ------------------------------------------------------------------ #
    # Public interface
    # ------------------------------------------------------------------ #
    async def chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        image_data: Optional[str] = None,
        file_content: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Main chat entry point used by dashboard and Telegram."""

        if not message and not file_content and not image_data:
            return {
                "message": "I'm ready whenever you are. Ask me about assignments, exams, schedules, or share a file.",
                "metadata": {"timestamp": datetime.now().isoformat()},
            }

        messages: List[BaseMessage] = []
        if conversation_history:
            for turn in conversation_history[-12:]:
                role = turn.get("role")
                content = (turn.get("content") or "").strip()
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))

        current_content: List[Dict[str, Any]] = []
        if message:
            current_content.append({"type": "text", "text": message})
        if image_data:
            current_content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                }
            )
        if file_content:
            current_content.append(
                {"type": "text", "text": f"\n\n**Uploaded File Content:**\n{file_content}"}
            )

        if len(current_content) == 1 and current_content[0]["type"] == "text":
            messages.append(HumanMessage(content=current_content[0]["text"]))
        else:
            messages.append(HumanMessage(content=current_content))

        messages = [self._system_message()] + messages

        metadata_flags = {"used_tools": set(), "timestamp": datetime.now().isoformat()}

        try:
            response = self._run_tool_loop(messages, metadata_flags)
            metadata = {
                "timestamp": metadata_flags["timestamp"],
                "tools_invoked": sorted(metadata_flags["used_tools"]),
                "used_notion_data": any(
                    tool in metadata_flags["used_tools"]
                    for tool in [
                        "fetch_assignments",
                        "fetch_exams",
                        "fetch_weekly_schedule",
                        "fetch_courses",
                        "search_notion_notes",
                    ]
                ),
                "used_knowledge_base": any(
                    tool in metadata_flags["used_tools"]
                    for tool in ["search_course_materials", "get_course_material", "list_material_courses"]
                ),
                "used_search": "web_search" in metadata_flags["used_tools"],
                "used_logs": "fetch_logs" in metadata_flags["used_tools"],
            }
            return {"message": response, "metadata": metadata}
        except Exception as exc:
            logger.error("UltronAgent.chat failed: %s", exc)
            return {
                "message": f"I ran into an unexpected issue: {exc}. Please try again.",
                "metadata": {"error": True, "timestamp": datetime.now().isoformat()},
            }

    async def analyze_image(self, image_data: str, query: str = "What's in this image?") -> str:
        response = await self.chat(message=query, image_data=image_data)
        return response["message"]

    def get_conversation_summary(self, messages: List[Dict[str, str]]) -> str:
        try:
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", "Summarize the following conversation in 2-3 sentences."),
                    ("user", "{conversation}"),
                ]
            )
            conversation_text = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
            chain = prompt | self.llm
            summary = chain.invoke({"conversation": conversation_text})
            return summary.content
        except Exception as exc:
            logger.error("Failed to summarize conversation: %s", exc)
            return "Unable to generate summary."

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _run_tool_loop(self, messages: List[BaseMessage], metadata_flags: Dict[str, Any]) -> str:
        loop_messages = list(messages)

        while True:
            ai_message: AIMessage = self.llm_with_tools.invoke(loop_messages)
            loop_messages.append(ai_message)

            if not getattr(ai_message, "tool_calls", None):
                return ai_message.content

            for call in ai_message.tool_calls:
                if isinstance(call, dict):
                    function_payload = call.get("function") or {}
                    name = function_payload.get("name") or call.get("name")
                    raw_args = function_payload.get("arguments") or call.get("arguments") or "{}"
                else:
                    name = getattr(call, "name", None)
                    raw_args = getattr(call, "arguments", None)
                    function_payload = getattr(call, "function", None)
                    if function_payload:
                        name = getattr(function_payload, "name", name)
                        raw_args = getattr(function_payload, "arguments", raw_args)

                if not name:
                    logger.warning("Tool call missing name: %s", call)
                    continue

                try:
                    args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args or {}
                except json.JSONDecodeError:
                    logger.warning("Failed to parse tool arguments for %s: %s", name, raw_args)
                    args = {}

                invocation = ToolInvocation(tool=name, tool_input=args or {})
                try:
                    tool_result = self.tool_executor.invoke(invocation)
                except Exception as exc:
                    logger.error("Tool %s invocation failed: %s", name, exc)
                    tool_result = {"error": str(exc)}

                metadata_flags["used_tools"].add(name)

                call_id = call.get("id") if isinstance(call, dict) else getattr(call, "id", None)
                if not call_id:
                    call_id = f"{name}_{len(loop_messages)}"
                    logger.warning("Tool call missing id; using fallback %s", call_id)

                if isinstance(tool_result, (dict, list)):
                    content = json.dumps(tool_result, ensure_ascii=False)
                else:
                    content = str(tool_result)

                loop_messages.append(ToolMessage(content=content, tool_call_id=call_id, name=name))

    def _system_message(self) -> BaseMessage:
        system_content = """You are Ultron, an advanced academic AI assistant built to support a university student.
Your primary directive is to protect and improve the student's academic success.

Core Capabilities:
- Retrieve assignments, exams, announcements, and schedules from internal tools when helpful.
- Use Google Calendar data when available; fall back to Notion.
- Perform web searches for up-to-date information when internal data is insufficient.
- Analyse uploaded documents or images and incorporate their contents.
- Track deadlines precisely (show days and hours remaining) and surface urgent priorities (<3 days).
- Provide clear next steps, study advice, or scheduling recommendations.

Behavior:
- If you call internal tools, always acknowledge the source in the final answer.
- Keep explanations structured and encouraging.
- If data is missing, say so and suggest alternatives.
- Default to English unless the user switches to Turkish; match their language."""
        return SystemMessage(content=system_content)

    def _filter_by_days(self, items: List[Dict[str, Any]], key: str, days: int) -> List[Dict[str, Any]]:
        try:
            cutoff = datetime.now() + timedelta(days=days)
        except Exception:
            return items

        filtered: List[Dict[str, Any]] = []
        for item in items:
            value = item.get(key)
            if not value:
                filtered.append(item)
                continue
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except Exception:
                filtered.append(item)
                continue
            if parsed <= cutoff:
                filtered.append(item)
        return filtered

    @staticmethod
    def _to_json(data: Any) -> str:
        try:
            return json.dumps(data, ensure_ascii=False)
        except TypeError:
            return json.dumps(json.loads(json.dumps(data, default=str)), ensure_ascii=False)

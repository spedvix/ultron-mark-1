from __future__ import annotations

import textwrap
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI

from ..settings import settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


class ChatService:
    """Generate Ultron chat responses with OpenAI."""

    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY must be configured to use the chat service.")

        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_chat_model or "gpt-5-mini"
        self._system_prompt = textwrap.dedent(
            """
            You are Ultron, an academic copilot for university students in Istanbul.
            Offer concise, encouraging guidance grounded in practical steps. Whenever
            a deadline or date is mentioned, convert it to the student's local context
            (Europe/Istanbul) and surface urgency if relevant. If additional context
            about assignments, exams, announcements, or schedules is provided, use it
            responsibly; otherwise, acknowledge when information is not available.
            """
        ).strip()

    async def generate_reply(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        attachment: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a response from the assistant.

        Args:
            message: Latest user message.
            history: Prior conversation turns as dicts with ``role`` and ``content``.
            attachment: Optional processed file data to weave into the prompt.
            context: Optional dict with structured academic data.
        """
        if not message and not attachment:
            return {
                "message": "I'm ready when you are. How can I help with your classes today?",
                "metadata": {"model": self._model, "tokens": 0},
            }

        prompt_history = [{"role": "system", "content": self._system_prompt}]
        if history:
            for turn in history[-12:]:
                role = turn.get("role")
                content = (turn.get("content") or "").strip()
                if role in {"user", "assistant"} and content:
                    prompt_history.append({"role": role, "content": content})

        user_message = message or "Please review the attached file."
        user_message = self._augment_with_attachment(user_message, attachment)
        user_message = self._augment_with_context(user_message, context)

        # Ensure the most recent entry is the current user message
        if not prompt_history or prompt_history[-1]["role"] != "user":
            prompt_history.append({"role": "user", "content": user_message})
        else:
            prompt_history[-1]["content"] = user_message

        logger.debug("Calling OpenAI with model %s", self._model)
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=prompt_history,
            temperature=0.7,
            max_completion_tokens=900,
        )

        assistant_message = response.choices[0].message.content.strip()
        usage = getattr(response, "usage", None)
        total_tokens = usage.total_tokens if usage else None

        metadata = {"model": self._model}
        if total_tokens is not None:
            metadata["tokens"] = total_tokens
        if attachment and attachment.get("filename"):
            metadata["attachment"] = attachment["filename"]

        return {
            "message": assistant_message,
            "metadata": metadata,
        }

    def _augment_with_attachment(self, message: str, attachment: Optional[Dict[str, Any]]) -> str:
        if not attachment or not attachment.get("type"):
            return message

        filename = attachment.get("filename", "attachment")
        file_type = attachment.get("type")
        size = attachment.get("size")
        summary_lines = [f"[Attachment: {filename} | type: {file_type} | size: {size} bytes]"]

        if file_type == "image":
            summary_lines.append(
                "The user shared an image. Vision analysis is not available in this mode, "
                "so provide textual guidance based on their description or ask follow-up questions."
            )
        else:
            content = attachment.get("content") or ""
            if content:
                excerpt = content[:4000]
                summary_lines.append("Attachment excerpts:\n" + excerpt)

        return message + "\n\n" + "\n".join(summary_lines)

    def _augment_with_context(self, message: str, context: Optional[Dict[str, Any]]) -> str:
        if not context:
            return message

        try:
            serialized = textwrap.shorten(str(context), width=1800, placeholder=" ...")
            return message + f"\n\n[Academic Context]\n{serialized}"
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("Failed to serialize context: %s", exc)
            return message

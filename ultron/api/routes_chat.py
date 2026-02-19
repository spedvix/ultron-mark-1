from __future__ import annotations

import json
from functools import lru_cache
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from ..services.chat_service import ChatService
from ..settings import settings

try:
    from src.ai.file_processor import FileProcessor  # type: ignore
except ImportError:  # pragma: no cover - dashboard package optional
    FileProcessor = None  # type: ignore

router = APIRouter()


@lru_cache(maxsize=1)
def get_chat_service() -> ChatService:
    return ChatService()


def _load_history(raw: Optional[str]) -> list[dict[str, str]]:
    if not raw:
        return []
    try:
        payload = json.loads(raw)
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
    except json.JSONDecodeError:
        pass
    return []


async def _process_upload(file: UploadFile | None) -> Optional[Dict[str, Any]]:
    if file is None:
        return None
    if FileProcessor is None:
        raise HTTPException(status_code=501, detail="File support is not available.")

    data = await file.read()
    result = FileProcessor.process_file(data, file.filename)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to process file."))
    return result


@router.post("/chat")
async def chat_completion(
    message: str = Form(default=""),
    conversation_history: Optional[str] = Form(default=None),
    file: UploadFile | None = File(default=None),
    chat_service: ChatService = Depends(get_chat_service),
):
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="Chat service is not configured.")

    history = _load_history(conversation_history)
    attachment = await _process_upload(file)

    reply = await chat_service.generate_reply(
        message=message,
        history=history,
        attachment=attachment,
    )
    return reply

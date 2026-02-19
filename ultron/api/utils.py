from __future__ import annotations

from datetime import datetime, timezone

from ..settings import settings


def determine_urgency(due_ts: datetime, now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    if due_ts.tzinfo is None:
        due_ts = due_ts.replace(tzinfo=timezone.utc)
    delta = due_ts - now
    hours = delta.total_seconds() / 3600
    if hours < 48:
        return "critical"
    if hours < 96:
        return "warning"
    return "normal"


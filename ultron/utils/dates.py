from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def local_now(tz_name: str) -> datetime:
    """Return a timezone-aware now() for provided zone."""
    return datetime.now(tz=ZoneInfo(tz_name))


def as_timezone(dt: datetime, tz_name: str) -> datetime:
    """Convert datetime to the provided timezone."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(ZoneInfo(tz_name))


def to_utc(dt: datetime) -> datetime:
    """Convert datetime to UTC timezone."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


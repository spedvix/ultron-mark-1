from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select

from ..api.deps import get_repository
from ..api.utils import determine_urgency
from ..db.models import Artifact
from ..db.repo import Repository
from ..settings import settings
from ..utils.dates import as_timezone

router = APIRouter()


@router.get("/daily")
async def daily_brief(
    tz: str = Query(default=settings.timezone, description="IANA timezone name"),
    repo: Repository = Depends(get_repository),
) -> dict[str, object]:
    target_tz = ZoneInfo(tz)
    now_local = datetime.now(target_tz)
    now_utc = now_local.astimezone(timezone.utc)

    upcoming = repo.deadlines_next_hours(72)
    brief_deadlines = [
        {
            "id": deadline.id,
            "course": deadline.course.code if deadline.course else None,
            "kind": deadline.artifact.kind.value,
            "title": deadline.title,
            "due_ts": deadline.due_ts.astimezone(target_tz).isoformat(),
            "source": deadline.artifact.source,
            "url": deadline.artifact.url,
            "urgency": determine_urgency(deadline.due_ts, now_utc),
        }
        for deadline in upcoming
    ]

    twenty_four_hours_ago = now_utc - timedelta(hours=24)
    stmt = select(Artifact).where(Artifact.discovered_ts >= twenty_four_hours_ago).order_by(Artifact.discovered_ts.desc()).limit(20)
    new_artifacts = [
        {
            "kind": artifact.kind.value,
            "title": artifact.title,
            "url": artifact.url,
        }
        for artifact in repo.session.execute(stmt).scalars()
    ]

    conflicts = _detect_conflicts(upcoming, target_tz)

    return {
        "date": now_local.date().isoformat(),
        "due_next_72h": brief_deadlines,
        "new_artifacts": new_artifacts,
        "conflicts": conflicts,
    }


def _detect_conflicts(deadlines, tz: ZoneInfo) -> list[dict[str, str]]:
    conflicts: list[dict[str, str]] = []
    seen = set()
    for idx, a in enumerate(deadlines):
        for b in deadlines[idx + 1 :]:
            delta = abs((a.due_ts - b.due_ts).total_seconds())
            if delta <= 3600:  # within an hour
                key = tuple(sorted([a.id, b.id]))
                if key in seen:
                    continue
                seen.add(key)
                conflicts.append(
                    {
                        "a": f"{a.title} ({a.due_ts.astimezone(tz).isoformat()})",
                        "b": f"{b.title} ({b.due_ts.astimezone(tz).isoformat()})",
                    }
                )
    return conflicts


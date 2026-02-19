from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel
from sqlalchemy import select

from ..api.deps import get_repository
from ..api.utils import determine_urgency
from ..db.models import Deadline, DeadlineStatus
from ..db.repo import Repository
from ..settings import settings
from ..google.calendar_service import GoogleCalendarService

router = APIRouter()
calendar_service = GoogleCalendarService()


class DeadlineStatusUpdate(BaseModel):
    status: DeadlineStatus


@router.get("/upcoming")
async def upcoming_deadlines(
    days: int = Query(default=14, ge=1, le=60),
    tz: str = Query(default=settings.timezone),
    repo: Repository = Depends(get_repository),
) -> list[dict[str, object]]:
    target_tz = ZoneInfo(tz)
    now = datetime.now(timezone.utc)
    results = []

    if calendar_service.client:
        deadlines = calendar_service.upcoming_deadlines(days)
        for deadline in deadlines:
            local_due = deadline.start.astimezone(target_tz)
            results.append(
                {
                    "id": deadline.event_id,
                    "title": deadline.title,
                    "course": deadline.course,
                    "kind": deadline.kind,
                    "due_ts": local_due.isoformat(),
                    "location": deadline.location,
                    "status": deadline.status,
                    "urgency": determine_urgency(deadline.start.astimezone(timezone.utc), now),
                    "source": "google_calendar",
                    "url": deadline.url,
                }
            )
        return results

    deadlines = repo.upcoming_deadlines(days, tz)
    results = []
    for deadline in deadlines:
        local_due = deadline.due_ts.astimezone(target_tz)
        results.append(
            {
                "id": deadline.id,
                "title": deadline.title,
                "course": deadline.course.code if deadline.course else None,
                "kind": deadline.artifact.kind.value,
                "due_ts": local_due.isoformat(),
                "location": deadline.location,
                "status": deadline.status.value,
                "urgency": determine_urgency(deadline.due_ts, now),
                "source": deadline.artifact.source,
                "url": deadline.artifact.url,
            }
        )
    return results


@router.post("/{deadline_id}/status")
async def update_deadline_status(
    deadline_id: str = Path(..., description="Deadline identifier"),
    payload: DeadlineStatusUpdate = ...,
    repo: Repository = Depends(get_repository),
) -> dict[str, object]:
    stmt = select(Deadline).where(Deadline.id == deadline_id)
    deadline = repo.session.execute(stmt).scalar_one_or_none()
    if not deadline:
        raise HTTPException(status_code=404, detail="Deadline not found")

    deadline.status = payload.status
    repo.session.commit()
    return {"id": deadline_id, "status": payload.status.value}


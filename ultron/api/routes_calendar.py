from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import select

from ..api.deps import get_repository
from ..api.utils import determine_urgency
from ..db.models import Deadline, DeadlineStatus
from ..db.repo import Repository
from ..google.calendar_service import GoogleCalendarService
from ..settings import settings

router = APIRouter()
ics_router = APIRouter()
calendar_service = GoogleCalendarService()


@router.get("/weekly")
async def weekly_schedule(
    tz: str = Query(default=settings.timezone, description="IANA timezone name"),
    repo: Repository = Depends(get_repository),
) -> list[dict[str, object]]:
    target_tz = ZoneInfo(tz)
    now_local = datetime.now(target_tz)
    now_utc = now_local.astimezone(timezone.utc)
    grouped = {day: {"deadlines": [], "classes": []} for day in range(7)}

    if calendar_service.client:
        deadlines = calendar_service.upcoming_deadlines(7)
        for deadline in deadlines:
            local_due = deadline.start.astimezone(target_tz)
            offset = (local_due.date() - now_local.date()).days
            if 0 <= offset < 7:
                grouped[offset]["deadlines"].append(
                    {
                        "id": deadline.event_id,
                        "title": deadline.title,
                        "course": deadline.course,
                        "due_ts": local_due.isoformat(),
                        "urgency": determine_urgency(deadline.start.astimezone(timezone.utc), now_utc),
                    }
                )
    else:
        deadlines = repo.upcoming_deadlines(7, tz)
        for deadline in deadlines:
            local_due = deadline.due_ts.astimezone(target_tz)
            offset = (local_due.date() - now_local.date()).days
            if 0 <= offset < 7:
                grouped[offset]["deadlines"].append(
                    {
                        "id": deadline.id,
                        "title": deadline.title,
                        "course": deadline.course.code if deadline.course else None,
                        "due_ts": local_due.isoformat(),
                        "urgency": determine_urgency(deadline.due_ts, now_utc),
                    }
                )

    schedule: list[dict[str, object]] = []
    for offset in range(7):
        day_date = now_local.date() + timedelta(days=offset)
        schedule.append(
            {
                "date": day_date.isoformat(),
                "day": day_date.strftime("%A"),
                "is_today": offset == 0,
                "deadlines": sorted(grouped[offset]["deadlines"], key=lambda d: d["due_ts"]),
                "classes": grouped[offset]["classes"],
            }
        )
    return schedule


@ics_router.get("/")
async def ics_export(repo: Repository = Depends(get_repository)) -> Response:
    stmt = select(Deadline).where(Deadline.status == DeadlineStatus.OPEN)
    deadlines = list(repo.session.execute(stmt).scalars())
    now = datetime.now(timezone.utc)
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Ultron//EN",
        "CALSCALE:GREGORIAN",
    ]
    for deadline in deadlines:
        due_utc = deadline.due_ts.astimezone(timezone.utc)
        summary = _sanitize(deadline.title)
        description = _sanitize(deadline.artifact.title)
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{deadline.id}@ultron",
                f"DTSTAMP:{now.strftime('%Y%m%dT%H%M%SZ')}",
                f"DTSTART:{due_utc.strftime('%Y%m%dT%H%M%SZ')}",
                f"SUMMARY:{summary}",
                f"DESCRIPTION:{description}",
                f"URL:{deadline.artifact.url}",
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    payload = "\r\n".join(lines) + "\r\n"
    headers = {"Content-Disposition": 'attachment; filename="ultron_schedule.ics"'}
    return Response(content=payload, media_type="text/calendar", headers=headers)


def _sanitize(value: str) -> str:
    return value.replace("\n", " ").replace(",", "\\,").replace(";", "\\;")

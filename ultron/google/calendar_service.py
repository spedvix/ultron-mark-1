from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, List, Optional

from loguru import logger

from common.google_calendar import CalendarEvent, GoogleCalendarClient
from ..settings import settings

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    from backports.zoneinfo import ZoneInfo  # type: ignore


@dataclass(slots=True)
class DeadlineEvent:
    event_id: str
    title: str
    start: datetime
    end: datetime
    kind: str
    course: Optional[str]
    location: Optional[str]
    url: Optional[str]
    status: str
    description: Optional[str]


class GoogleCalendarService:
    """Expose Google Calendar data for backend APIs."""

    def __init__(self):
        token_file = settings.google_calendar_token_file
        self.assignments_calendar = settings.google_calendar_assignments_id
        self.exams_calendar = settings.google_calendar_exams_id or settings.google_calendar_assignments_id
        self.schedule_calendar = settings.google_calendar_schedule_id or settings.google_calendar_assignments_id
        self.timezone = self._load_timezone(settings.google_calendar_timezone)

        if token_file:
            try:
                self.client = GoogleCalendarClient(token_file)
            except Exception as exc:  # pragma: no cover
                logger.error("Unable to initialise Google Calendar client: %s", exc)
                self.client = None
        else:
            logger.warning("GOOGLE_CALENDAR_TOKEN_FILE missing; Google Calendar integration disabled")
            self.client = None

    def upcoming_deadlines(self, days: int) -> List[DeadlineEvent]:
        events: List[DeadlineEvent] = []
        events.extend(self._fetch_as_deadlines(self.assignments_calendar, "assignment", days))
        events.extend(self._fetch_as_deadlines(self.exams_calendar, "exam", days))
        events.sort(key=lambda item: item.start)
        return events

    def weekly_schedule(self, days: int = 7) -> Dict[int, List[DeadlineEvent]]:
        """Return deadlines grouped by day offset from today."""
        assignments = self._fetch_as_deadlines(self.assignments_calendar, "assignment", days)
        exams = self._fetch_as_deadlines(self.exams_calendar, "exam", days)
        combined = assignments + exams

        grouped: Dict[int, List[DeadlineEvent]] = {offset: [] for offset in range(days)}
        now_local = self._now_local()
        today = now_local.date()

        for item in combined:
            local_start = item.start.astimezone(self.timezone)
            offset = (local_start.date() - today).days
            if 0 <= offset < days:
                grouped[offset].append(item)

        for bucket in grouped.values():
            bucket.sort(key=lambda evt: evt.start)
        return grouped

    def _fetch_as_deadlines(self, calendar_id: Optional[str], kind: str, days: int) -> List[DeadlineEvent]:
        if not calendar_id or not self.client:
            return []
        now = datetime.now(timezone.utc)
        horizon = now + timedelta(days=days)
        try:
            events = self.client.events(
                calendar_id,
                time_min=now,
                time_max=horizon,
                single_events=True,
                order_by="startTime",
            )
        except Exception as exc:
            logger.error("Google Calendar fetch failed for %s: %s", calendar_id, exc)
            return []
        deadlines: List[DeadlineEvent] = []
        for event in events:
            deadlines.append(self._to_deadline_event(event, kind))
        return deadlines

    def _to_deadline_event(self, event: CalendarEvent, kind: str) -> DeadlineEvent:
        start_local = self._to_local(event.start)
        end_local = self._to_local(event.end)
        return DeadlineEvent(
            event_id=event.event_id,
            title=event.summary,
            start=start_local,
            end=end_local,
            kind=kind,
            course=self._extract_course(event),
            location=event.location,
            url=event.link,
            status=event.raw.get("status", "confirmed"),
            description=event.description,
        )

    def _to_local(self, dt: datetime) -> datetime:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(self.timezone)

    def _now_local(self) -> datetime:
        return datetime.now(self.timezone)

    @staticmethod
    def _extract_course(event: CalendarEvent) -> Optional[str]:
        extended = event.raw.get("extendedProperties", {}).get("private", {})
        if isinstance(extended, dict):
            course = extended.get("course")
            if course:
                return course
        if event.location:
            return event.location
        if event.description:
            return event.description.strip().splitlines()[0][:80]
        return None

    @staticmethod
    def _load_timezone(name: Optional[str]) -> ZoneInfo:
        if not name:
            return ZoneInfo("UTC")
        try:
            return ZoneInfo(name)
        except Exception:  # pragma: no cover
            logger.warning("Invalid timezone '%s' for Google Calendar, defaulting to UTC", name)
            return ZoneInfo("UTC")


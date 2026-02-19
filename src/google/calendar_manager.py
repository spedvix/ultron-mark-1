from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from loguru import logger

from common.google_calendar import CalendarEvent, GoogleCalendarClient
from src.config.settings import settings

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    from backports.zoneinfo import ZoneInfo  # type: ignore


class GoogleCalendarManager:
    """Access Google Calendar events relevant to the Ultron dashboard."""

    def __init__(self):
        token_file = settings.GOOGLE_CALENDAR_TOKEN_FILE
        self.timezone = self._load_timezone(settings.GOOGLE_CALENDAR_TIMEZONE)
        self.assignments_calendar = settings.GOOGLE_CALENDAR_ASSIGNMENTS_ID
        self.exams_calendar = settings.GOOGLE_CALENDAR_EXAMS_ID or settings.GOOGLE_CALENDAR_ASSIGNMENTS_ID
        self.schedule_calendar = settings.GOOGLE_CALENDAR_SCHEDULE_ID or settings.GOOGLE_CALENDAR_ASSIGNMENTS_ID

        if token_file:
            try:
                self.client = GoogleCalendarClient(token_file)
            except Exception as exc:  # pragma: no cover - defensive
                logger.error("Failed to initialize Google Calendar client: %s", exc)
                self.client = None
        else:
            logger.warning("GOOGLE_CALENDAR_TOKEN_FILE is not configured; Google Calendar features disabled")
            self.client = None

    # Public API ---------------------------------------------------------
    def get_assignments(self, days_ahead: int = 14) -> List[Dict]:
        events = self._fetch_events(self.assignments_calendar, days_ahead)
        assignments: List[Dict] = []
        for event in events:
            start_local = self._to_local(event.start)
            assignments.append(
                {
                    "id": event.event_id,
                    "title": event.summary,
                    "course": self._extract_course(event),
                    "due_date": start_local.isoformat(),
                    "status": event.raw.get("status", "confirmed"),
                    "url": event.link,
                    "location": event.location,
                    "description": event.description,
                }
            )
        assignments.sort(key=lambda item: item["due_date"])
        return assignments

    def get_exams(self, days_ahead: int = 60) -> List[Dict]:
        events = self._fetch_events(self.exams_calendar, days_ahead)
        exams: List[Dict] = []
        for event in events:
            start_local = self._to_local(event.start)
            exams.append(
                {
                    "id": event.event_id,
                    "title": event.summary,
                    "course": self._extract_course(event),
                    "date": start_local.isoformat(),
                    "type": event.raw.get("eventType", "exam"),
                    "location": event.location,
                    "url": event.link,
                    "description": event.description,
                }
            )
        exams.sort(key=lambda item: item["date"])
        return exams

    def get_weekly_events(self) -> Dict[str, List[Dict]]:
        """Return events grouped by weekday for the next 7 days."""
        events = self._fetch_events(self.schedule_calendar, days_ahead=7)
        grouped: Dict[str, List[Dict]] = defaultdict(list)
        for event in events:
            start_local = self._to_local(event.start)
            end_local = self._to_local(event.end)
            day_key = start_local.strftime("%A")
            grouped[day_key].append(
                {
                    "id": event.event_id,
                    "name": event.summary,
                    "start_time": start_local.strftime("%H:%M"),
                    "end_time": end_local.strftime("%H:%M"),
                    "schedule": f"{start_local.strftime('%H:%M')} - {end_local.strftime('%H:%M')}",
                    "room": event.location,
                    "description": event.description,
                    "link": event.link,
                }
            )
        ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day in ordered_days:
            grouped.setdefault(day, [])
        for entries in grouped.values():
            entries.sort(key=lambda item: item["start_time"])
        return {day: grouped[day] for day in ordered_days}

    # Internal helpers ---------------------------------------------------
    def _fetch_events(self, calendar_id: str, days_ahead: int) -> List[CalendarEvent]:
        if not self.client or not calendar_id:
            return []
        now = datetime.now(timezone.utc)
        horizon = now + timedelta(days=days_ahead)
        try:
            return self.client.events(
                calendar_id,
                time_min=now,
                time_max=horizon,
                single_events=True,
                order_by="startTime",
            )
        except Exception as exc:
            logger.error("Unable to fetch Google Calendar events for %s: %s", calendar_id, exc)
            return []

    def _to_local(self, dt: datetime) -> datetime:
        if not self.timezone:
            return dt
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(self.timezone)

    @staticmethod
    def _load_timezone(name: str) -> Optional[ZoneInfo]:
        if not name:
            return None
        try:
            return ZoneInfo(name)
        except Exception:  # pragma: no cover - invalid timezone fallback
            logger.warning("Invalid timezone '%s' provided for Google Calendar; using UTC", name)
            return ZoneInfo("UTC")

    @staticmethod
    def _extract_course(event: CalendarEvent) -> Optional[str]:
        extended = event.raw.get("extendedProperties", {}).get("private", {})
        course = extended.get("course") if isinstance(extended, dict) else None
        if course:
            return course
        if event.location:
            return event.location
        if event.description:
            line = event.description.strip().splitlines()[0]
            return line[:80]
        return None

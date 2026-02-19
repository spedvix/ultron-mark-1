from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from loguru import logger


SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


@dataclass(slots=True)
class CalendarEvent:
    event_id: str
    summary: str
    start: datetime
    end: datetime
    description: Optional[str]
    location: Optional[str]
    link: Optional[str]
    raw: dict


class GoogleCalendarClient:
    """Lightweight wrapper around the Google Calendar API."""

    def __init__(self, token_path: str, scopes: Optional[Iterable[str]] = None):
        if not token_path:
            raise ValueError("Google Calendar token path must be configured")
        self.token_path = token_path
        self.scopes = list(scopes) if scopes else SCOPES
        self._service = None

    def events(
        self,
        calendar_id: str,
        *,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: Optional[int] = None,
        include_cancelled: bool = False,
        single_events: bool = True,
        order_by: str = "startTime",
    ) -> List[CalendarEvent]:
        if not calendar_id:
            raise ValueError("Calendar ID must be provided")
        params = {
            "calendarId": calendar_id,
            "singleEvents": single_events,
            "orderBy": order_by,
            "showDeleted": include_cancelled,
        }
        if time_min:
            params["timeMin"] = self._ensure_utc(time_min).isoformat()
        if time_max:
            params["timeMax"] = self._ensure_utc(time_max).isoformat()
        if max_results:
            params["maxResults"] = max_results

        service = self._get_service()
        events: List[CalendarEvent] = []
        page_token: Optional[str] = None

        while True:
            try:
                response = service.events().list(pageToken=page_token, **params).execute()
            except HttpError as exc:
                logger.error("Google Calendar API error: %s", exc)
                raise
            for item in response.get("items", []):
                events.append(self._to_event(item))
            page_token = response.get("nextPageToken")
            if not page_token:
                break

        return events

    def _get_service(self):
        if self._service is None:
            creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
            self._service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        return self._service

    @staticmethod
    def _ensure_utc(dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    @staticmethod
    def _parse_dt(payload: dict) -> datetime:
        value = payload.get("dateTime")
        if value:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        date_value = payload.get("date")
        if date_value:
            return datetime.fromisoformat(f"{date_value}T00:00:00+00:00")
        raise ValueError("Event payload missing start/end datetime")

    def _to_event(self, payload: dict) -> CalendarEvent:
        start = self._parse_dt(payload.get("start", {}))
        end_payload = payload.get("end", {})
        try:
            end = self._parse_dt(end_payload)
        except ValueError:
            end = start + timedelta(hours=1)
        return CalendarEvent(
            event_id=payload.get("id", ""),
            summary=payload.get("summary", "Untitled event"),
            start=start,
            end=end,
            description=payload.get("description"),
            location=payload.get("location"),
            link=payload.get("htmlLink"),
            raw=payload,
        )


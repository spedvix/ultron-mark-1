from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, Optional


@dataclass(slots=True)
class EmailMessage:
    id: str
    thread_id: Optional[str]
    subject: str
    sender: str
    date: datetime
    text: str
    html: Optional[str]
    headers: Mapping[str, str]


@dataclass(slots=True)
class AnnouncementItem:
    source: str
    title: str
    url: str
    published_ts: datetime
    body: str
    summary: Optional[str] = None


@dataclass(slots=True)
class NotionItem:
    page_id: str
    title: str
    url: str
    last_edited: datetime
    content: str
    course_code: Optional[str] = None

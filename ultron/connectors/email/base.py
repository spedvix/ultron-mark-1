from __future__ import annotations

import abc
import re
from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Optional

from ...db.repo import Repository
from ...settings import settings
from ..types import EmailMessage

EMAIL_KEYWORDS = re.compile(
    r"\b(syllabus|assignment|homework|hw|quiz|exam|make-?up|midterm|final|deadline|submit|section|class|cancelled)\b",
    re.IGNORECASE,
)


class EmailConnector(abc.ABC):
    """Base class for email connectors."""

    source_name: str
    window_days: int = 60

    def __init__(self, mailbox: str = "INBOX"):
        self.mailbox = mailbox

    @abc.abstractmethod
    def sync(self, repo: Repository) -> List[EmailMessage]:
        """Synchronise emails with the backing store."""

    @staticmethod
    def should_keep(subject: str, body_text: str) -> bool:
        """Return True if the message contains relevant keywords."""
        if EMAIL_KEYWORDS.search(subject or ""):
            return True
        return bool(EMAIL_KEYWORDS.search(body_text or ""))

    @staticmethod
    def cutoff_date(days: int = 60) -> datetime:
        return datetime.now(timezone.utc) - timedelta(days=days)

    def _update_cursor(self, repo: Repository, cursor: Optional[str], extra: Optional[str] = None) -> None:
        repo.set_sync_cursor(self.source_name, cursor, extra=extra)

    def _get_cursor(self, repo: Repository) -> Optional[str]:
        state = repo.get_sync_cursor(self.source_name)
        return state.cursor if state else None


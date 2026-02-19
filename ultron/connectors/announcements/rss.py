from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Iterable, List, Optional
from urllib.parse import urljoin

import feedparser
import httpx
from dateutil import parser as date_parser

from ...settings import settings
from ...utils.logging import get_logger
from ..types import AnnouncementItem

logger = get_logger(__name__)


class RSSAnnouncementConnector:
    """Fetch announcements from RSS/Atom feeds."""

    def __init__(self, base_urls: Optional[Iterable[str]] = None, rate_limit: float = 1.0):
        self.base_urls = list(base_urls or settings.ann_base_urls)
        self.rate_limit = rate_limit
        self._client = httpx.Client(timeout=15.0, headers={"User-Agent": "UltronBot/1.0"})

    def fetch(self) -> List[AnnouncementItem]:
        items: List[AnnouncementItem] = []
        for idx, url in enumerate(self.base_urls):
            try:
                response = self._client.get(url, follow_redirects=True)
                response.raise_for_status()
            except httpx.HTTPError as exc:
                logger.warning("Failed to fetch RSS feed %s: %s", url, exc)
                continue

            feed = feedparser.parse(response.text)
            for entry in feed.entries:
                published = self._resolve_published(entry)
                link = entry.get("link") or url
                summary = entry.get("summary", "")
                body = summary or entry.get("description", "")
                title = entry.get("title", link)
                items.append(
                    AnnouncementItem(
                        source=url,
                        title=title,
                        url=urljoin(url, link),
                        published_ts=published,
                        body=body,
                        summary=summary,
                    )
                )

            if idx < len(self.base_urls) - 1:
                time.sleep(max(self.rate_limit, 0.0))
        logger.info("RSS connector fetched %s announcement items", len(items))
        return items

    @staticmethod
    def _resolve_published(entry) -> datetime:
        if "published" in entry:
            try:
                return date_parser.parse(entry.published).astimezone(timezone.utc)
            except (ValueError, TypeError, OverflowError):
                pass
        if "updated" in entry:
            try:
                return date_parser.parse(entry.updated).astimezone(timezone.utc)
            except (ValueError, TypeError, OverflowError):
                pass
        return datetime.now(timezone.utc)

    def close(self) -> None:
        self._client.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


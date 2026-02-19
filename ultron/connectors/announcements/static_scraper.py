from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Dict, Iterable, List, Optional, Set
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from ...utils.logging import get_logger
from ..types import AnnouncementItem

logger = get_logger(__name__)


@dataclass
class SiteProfile:
    base: str
    card: str
    link: str
    title: str
    body: str
    date: str
    pagination: Optional[str | Callable[[BeautifulSoup], Optional[str]]] = None
    requires_js: bool = False


SITE_PROFILES: List[SiteProfile] = []


class StaticAnnouncementScraper:
    """Scrape static HTML pages for announcements."""

    def __init__(
        self,
        profiles: Optional[Iterable[SiteProfile]] = None,
        rate_limit: float = 1.0,
        max_pages: int = 5,
    ):
        self.profiles = list(profiles or SITE_PROFILES)
        self.rate_limit = rate_limit
        self.max_pages = max_pages
        self.client = httpx.Client(timeout=20.0, headers={"User-Agent": "UltronBot/1.0"})

    def fetch(self) -> List[AnnouncementItem]:
        items: List[AnnouncementItem] = []
        seen_urls: Set[str] = set()

        for profile in self.profiles:
            if profile.requires_js:
                logger.debug("Skipping %s because it requires JS rendering", profile.base)
                continue

            next_url: Optional[str] = profile.base
            pages = 0
            while next_url and pages < self.max_pages:
                try:
                    response = self.client.get(next_url)
                    response.raise_for_status()
                except httpx.HTTPError as exc:
                    logger.warning("Failed to fetch %s: %s", next_url, exc)
                    break

                soup = BeautifulSoup(response.text, "lxml")
                cards = soup.select(profile.card)
                for card in cards:
                    link_el = card.select_one(profile.link)
                    if not link_el:
                        continue
                    href = link_el.get("href")
                    if not href:
                        continue
                    href = urljoin(profile.base, href)
                    if href in seen_urls:
                        continue
                    seen_urls.add(href)

                    title_el = card.select_one(profile.title) if profile.title else link_el
                    body_el = card.select_one(profile.body) if profile.body else None
                    date_el = card.select_one(profile.date) if profile.date else None

                    title = title_el.get_text(strip=True) if title_el else href
                    body = body_el.get_text(" ", strip=True) if body_el else ""
                    published = self._parse_date(date_el.get_text(strip=True) if date_el else "")

                    items.append(
                        AnnouncementItem(
                            source=profile.base,
                            title=title,
                            url=href,
                            published_ts=published,
                            body=body,
                            summary=body[:140] + "..." if len(body) > 140 else body,
                        )
                    )

                pages += 1
                next_url = self._resolve_next(profile, soup)
                if next_url:
                    time.sleep(self.rate_limit)

        logger.info("Static scraper collected %s announcements", len(items))
        return items

    @staticmethod
    def _parse_date(value: str) -> datetime:
        if not value:
            return datetime.now(timezone.utc)
        try:
            return date_parser.parse(value).astimezone(timezone.utc)
        except (ValueError, TypeError, OverflowError):
            return datetime.now(timezone.utc)

    def _resolve_next(self, profile: SiteProfile, soup: BeautifulSoup) -> Optional[str]:
        if not profile.pagination:
            return None
        if isinstance(profile.pagination, str):
            next_el = soup.select_one(profile.pagination)
            if next_el and next_el.get("href"):
                return urljoin(profile.base, next_el["href"])
            return None
        try:
            result = profile.pagination(soup)
            if result:
                return urljoin(profile.base, result)
        except Exception as exc:  # pragma: no cover - user-provided callback
            logger.debug("Pagination callback failed: %s", exc)
        return None

    def close(self) -> None:
        self.client.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


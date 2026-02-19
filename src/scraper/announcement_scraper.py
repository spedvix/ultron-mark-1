"""
HTTP-based scraper for university announcements hosted on a public website.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from loguru import logger
from requests import Response
from requests.exceptions import RequestException, Timeout

from src.config.settings import settings


@dataclass(slots=True)
class Announcement:
    title: str
    date: str
    content: str
    link: Optional[str]

    def to_dict(self) -> Dict[str, str]:
        payload = {
            "title": self.title,
            "date": self.date,
            "content": self.content,
        }
        if self.link:
            payload["link"] = self.link
        return payload


class AnnouncementScraper:
    """Scrapes public announcements without requiring authentication."""

    def __init__(self, timeout: int = 15):
        self.url = settings.ANNOUNCEMENTS_URL or settings.UNI_WEBSITE_URL
        if not self.url:
            raise ValueError("Configure ANNOUNCEMENTS_URL or UNI_WEBSITE_URL for the announcement scraper")

        self.item_selector = settings.ANNOUNCEMENT_ITEM_SELECTOR or ".announcement-item"
        self.title_selector = settings.ANNOUNCEMENT_TITLE_SELECTOR or "h1, h2, h3"
        self.date_selector = settings.ANNOUNCEMENT_DATE_SELECTOR or ".announcement-date"
        self.content_selector = settings.ANNOUNCEMENT_CONTENT_SELECTOR or ".announcement-content, p"
        self.link_selector = settings.ANNOUNCEMENT_LINK_SELECTOR or "a"

        self.timeout = timeout
        self.session = requests.Session()
        logger.debug("AnnouncementScraper initialised for %s", self.url)

    # Public API ---------------------------------------------------------
    def scrape(self) -> List[Dict[str, str]]:
        """Fetch and parse announcements from the configured URL."""
        html = self._fetch_html()
        if not html:
            return []

        announcements = self._parse_html(html)
        logger.info("Announcement scraper produced %s items", len(announcements))
        return [item.to_dict() for item in announcements]

    # Internal helpers ---------------------------------------------------
    def _fetch_html(self, url: Optional[str] = None) -> str:
        target_url = url or self.url
        try:
            response: Response = self.session.get(target_url, timeout=self.timeout)
            response.raise_for_status()
            logger.debug("Fetched announcements page (%s)", response.status_code)
            return response.text
        except Timeout:
            logger.error("Announcement request to %s timed out after %ss", target_url, self.timeout)
        except RequestException as exc:
            logger.error("Failed to fetch announcements from %s: %s", target_url, exc)
        return ""

    def _parse_html(self, html: str) -> List[Announcement]:
        soup = BeautifulSoup(html, "html.parser")
        nodes = soup.select(self.item_selector)

        if not nodes:
            logger.warning("No announcement elements found with selector '%s'", self.item_selector)
            return []

        results: List[Announcement] = []
        for node in nodes:
            title = self._extract_text(node, self.title_selector)
            date = self._extract_text(node, self.date_selector)
            content = self._extract_text(node, self.content_selector, allow_fallback=True)
            link = self._extract_link(node)

            if not title and not content:
                continue

            announcement = Announcement(
                title=title or "Untitled announcement",
                date=date,
                content=content,
                link=link,
            )
            results.append(announcement)

        return results

    def _extract_text(self, node: Tag, selector: str, *, allow_fallback: bool = False) -> str:
        if selector:
            target = node.select_one(selector)
            if target:
                return target.get_text(strip=True)
        if allow_fallback:
            fallback = node.get_text(separator=" ", strip=True)
            return fallback
        return ""

    def _extract_link(self, node: Tag) -> Optional[str]:
        link_tag = None
        if self.link_selector:
            link_tag = node.select_one(self.link_selector)
        if not link_tag:
            link_tag = node.find("a", href=True)
        if not link_tag:
            return None

        href = link_tag.get("href")
        if not href:
            return None
        return urljoin(self.url, href)

    def fetch_full_content(self, link: str) -> Optional[str]:
        html = self._fetch_html(link)
        if not html:
            return None
        soup = BeautifulSoup(html, "html.parser")
        content_node = soup.select_one(self.content_selector) or soup.select_one(".o_wblog_read_text")
        if not content_node:
            return None
        return content_node.get_text(separator=" ", strip=True)


if __name__ == "__main__":
    scraper = AnnouncementScraper()
    for announcement in scraper.scrape():
        print(f"\nTitle: {announcement.get('title')}")
        print(f"Date: {announcement.get('date')}")
        print(f"Content: {announcement.get('content')[:120]}")
        print(f"Link: {announcement.get('link')}")

from __future__ import annotations

import re
import time
from datetime import datetime, timezone
from typing import Generator, Iterable, List, Optional

from notion_client import Client
from notion_client.errors import APIResponseError

from ..settings import settings
from ..utils.logging import get_logger
from .types import NotionItem

logger = get_logger(__name__)

COURSE_CODE_RE = re.compile(r"\b[A-Za-z]{2,4}\s?-?\s?\d{3}\b")


class NotionConnector:
    """Fetch course content from Notion pages."""

    def __init__(self, api_key: Optional[str] = None, database_ids: Optional[Iterable[str]] = None, rate_limit: float = 0.5):
        self.api_key = api_key or settings.notion_api_key
        if not self.api_key:
            raise ValueError("NOTION_API_KEY must be configured")
        self.client = Client(auth=self.api_key)
        self.database_ids = [db for db in (database_ids or settings.notion_database_ids) if db]
        self.rate_limit = rate_limit

    def fetch(self) -> List[NotionItem]:
        items: List[NotionItem] = []
        try:
            if self.database_ids:
                for database_id in self.database_ids:
                    items.extend(self._iterate_database(database_id))
                    time.sleep(self.rate_limit)
            else:
                items.extend(self._search_pages())
        except APIResponseError as exc:
            logger.error("Notion API error: %s", exc)
            raise
        logger.info("Fetched %s Notion pages", len(items))
        return items

    def _iterate_database(self, database_id: str) -> List[NotionItem]:
        results: List[NotionItem] = []
        payload = self.client.databases.query(database_id=database_id)
        results.extend(self._pages_to_items(payload["results"]))
        while payload.get("has_more"):
            payload = self.client.databases.query(database_id=database_id, start_cursor=payload["next_cursor"])
            results.extend(self._pages_to_items(payload["results"]))
            time.sleep(self.rate_limit)
        return results

    def _search_pages(self) -> List[NotionItem]:
        results: List[NotionItem] = []
        payload = self.client.search(filter={"value": "page", "property": "object"})
        results.extend(self._pages_to_items(payload["results"]))
        while payload.get("has_more"):
            payload = self.client.search(
                filter={"value": "page", "property": "object"},
                start_cursor=payload["next_cursor"],
            )
            results.extend(self._pages_to_items(payload["results"]))
            time.sleep(self.rate_limit)
        return results

    def _pages_to_items(self, pages: Iterable[dict]) -> List[NotionItem]:
        items: List[NotionItem] = []
        for page in pages:
            page_id = page["id"]
            title = self._extract_title(page)
            if not title:
                continue
            content = self._collect_content(page_id)
            url = page.get("url", "")
            last_edited = datetime.fromisoformat(page["last_edited_time"].replace("Z", "+00:00")).astimezone(timezone.utc)
            course_code = self._detect_course_code(title, content)
            items.append(
                NotionItem(
                    page_id=page_id,
                    title=title,
                    url=url,
                    last_edited=last_edited,
                    content=content,
                    course_code=course_code,
                )
            )
        return items

    def _collect_content(self, page_id: str) -> str:
        lines: List[str] = []
        stack = [page_id]
        while stack:
            current = stack.pop()
            cursor: Optional[str] = None
            while True:
                children = self.client.blocks.children.list(block_id=current, start_cursor=cursor)
                for child in children.get("results", []):
                    text = self._block_to_text(child)
                    if text:
                        lines.append(text)
                    if child.get("has_children"):
                        stack.append(child["id"])
                if not children.get("has_more"):
                    break
                cursor = children.get("next_cursor")
                time.sleep(self.rate_limit)
        return "\n".join(lines)

    @staticmethod
    def _block_to_text(block: dict) -> str:
        block_type = block.get("type")
        data = block.get(block_type, {})
        rich_text = data.get("rich_text", [])
        fragments: List[str] = []
        for item in rich_text:
            fragments.append(item.get("plain_text", ""))
        return " ".join(fragments).strip()

    @staticmethod
    def _extract_title(page: dict) -> Optional[str]:
        properties = page.get("properties", {})
        for prop in properties.values():
            if prop.get("type") == "title":
                fragments = [frag.get("plain_text", "") for frag in prop.get("title", [])]
                title = "".join(fragments).strip()
                if title:
                    return title
        return None

    @staticmethod
    def _detect_course_code(title: str, content: str) -> Optional[str]:
        for text in (title, content):
            match = COURSE_CODE_RE.search(text)
            if match:
                return match.group(0).replace(" ", "").replace("-", "").upper()
        return None

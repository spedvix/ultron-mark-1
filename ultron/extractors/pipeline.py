from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Iterable, List, Optional, Tuple

from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from ..connectors.types import AnnouncementItem, EmailMessage, NotionItem
from ..db.models import Artifact, ArtifactKind, Deadline
from ..db.repo import ArtifactPayload, DeadlinePayload, Repository
from ..settings import settings
from ..utils.dates import to_utc
from ..utils.hashing import hash_text
from .llm_stub import normalize_artifact
from .rules import RuleExtractor, collapse_whitespace


@dataclass
class PipelineResult:
    artifacts: List[Artifact] = field(default_factory=list)
    deadlines: List[Deadline] = field(default_factory=list)

    def extend(self, other: "PipelineResult") -> None:
        self.artifacts.extend(other.artifacts)
        self.deadlines.extend(other.deadlines)


class ExtractionPipeline:
    def __init__(self, repo: Repository, timezone: Optional[str] = None):
        self.repo = repo
        self.rule_extractor = RuleExtractor()
        self.timezone = timezone or settings.timezone

    # Email ------------------------------------------------------------------
    def ingest_emails(self, messages: Iterable[EmailMessage], source: str = "imap") -> PipelineResult:
        result = PipelineResult()
        for message in messages:
            text = self._normalize_email_body(message)
            url = f"email://{message.id}"
            payload = self._process_artifact(
                title=message.subject or "Untitled email",
                text=text,
                url=url,
                published_ts=message.date,
                source=source,
                source_loc=message.id,
                fallback_kind=ArtifactKind.EMAIL,
                links=[],
            )
            if payload:
                artifact, deadlines = payload
                result.artifacts.append(artifact)
                result.deadlines.extend(deadlines)
        return result

    # Announcements ----------------------------------------------------------
    def ingest_announcements(self, items: Iterable[AnnouncementItem], source: str = "rss") -> PipelineResult:
        result = PipelineResult()
        for item in items:
            payload = self._process_artifact(
                title=item.title,
                text=item.body,
                url=item.url,
                published_ts=item.published_ts,
                source=source,
                source_loc=item.source,
                fallback_kind=ArtifactKind.ANNOUNCEMENT,
                links=[(item.url, item.summary or None)],
            )
            if payload:
                artifact, deadlines = payload
                result.artifacts.append(artifact)
                result.deadlines.extend(deadlines)
        return result

    # Notion -----------------------------------------------------------------
    def ingest_notion(self, items: Iterable[NotionItem], source: str = "notion") -> PipelineResult:
        result = PipelineResult()
        for item in items:
            payload = self._process_artifact(
                title=item.title,
                text=item.content,
                url=item.url,
                published_ts=item.last_edited,
                source=source,
                source_loc=item.page_id,
                fallback_kind=ArtifactKind.NOTION,
                links=[(item.url, "View in Notion")],
                explicit_course=item.course_code,
            )
            if payload:
                artifact, deadlines = payload
                result.artifacts.append(artifact)
                result.deadlines.extend(deadlines)
        return result

    # Core -------------------------------------------------------------------
    def _process_artifact(
        self,
        *,
        title: str,
        text: str,
        url: str,
        published_ts: datetime,
        source: str,
        source_loc: str,
        fallback_kind: ArtifactKind,
        links: List[Tuple[str, Optional[str]]],
        explicit_course: Optional[str] = None,
    ) -> Optional[Tuple[Artifact, List[Deadline]]]:
        normalized_text = collapse_whitespace(text)
        rule_hits = self.rule_extractor.extract(title, normalized_text)
        if explicit_course and explicit_course not in rule_hits.course_codes:
            rule_hits.course_codes.insert(0, explicit_course)
        norm = normalize_artifact(title, url, normalized_text, rule_hits)
        artifact_kind = self._resolve_kind(norm.kind, fallback_kind)
        hash_value = hash_text(url or "", normalized_text)
        published_ts = self._ensure_utc(published_ts)

        artifact_links = list(links)
        if norm.link:
            artifact_links.append((norm.link, "Source"))
        unique_links: dict[str, Optional[str]] = {}
        for href, label in artifact_links:
            if href not in unique_links:
                unique_links[href] = label
        artifact_links = [(href, unique_links[href]) for href in unique_links]

        artifact_payload = ArtifactPayload(
            kind=artifact_kind,
            title=norm.title or title,
            text=normalized_text,
            url=url or "",
            source=source,
            source_loc=source_loc,
            published_ts=published_ts,
            hash=hash_value,
            links=artifact_links,
        )
        artifact = self.repo.upsert_artifact(artifact_payload)
        deadlines: List[Deadline] = []
        if norm.due_iso:
            due_dt = self._parse_due(norm.due_iso)
            if due_dt:
                deadline_payload = DeadlinePayload(
                    artifact_hash=hash_value,
                    title=norm.title or title,
                    due_ts=due_dt,
                    tz=self.timezone,
                    confidence=norm.confidence,
                    location=norm.location,
                    course_code=norm.course_code,
                )
                deadline = self.repo.create_or_update_deadline(deadline_payload)
                deadlines.append(deadline)
        return artifact, deadlines

    def _resolve_kind(self, value: str, fallback: ArtifactKind) -> ArtifactKind:
        try:
            return ArtifactKind(value)
        except ValueError:
            return fallback

    def _parse_due(self, iso_value: str) -> Optional[datetime]:
        try:
            dt = date_parser.isoparse(iso_value)
        except (ValueError, TypeError):
            return None
        return to_utc(dt)

    def _ensure_utc(self, dt: datetime) -> datetime:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo(self.timezone))
        return to_utc(dt)

    @staticmethod
    def _normalize_email_body(message: EmailMessage) -> str:
        parts = [message.subject or "", message.text or ""]
        if message.html:
            parts.append(html_to_text(message.html))
        return "\n".join(part for part in parts if part)


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text(separator=" ", strip=True)

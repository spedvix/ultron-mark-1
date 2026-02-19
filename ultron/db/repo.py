from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Artifact, ArtifactKind, Course, Deadline, DeadlineStatus, Link, SyncState


@dataclass(slots=True)
class ArtifactPayload:
    kind: ArtifactKind
    title: str
    text: str
    url: str
    source: str
    source_loc: Optional[str]
    published_ts: datetime
    hash: str
    links: Iterable[tuple[str, Optional[str]]] = field(default_factory=list)


@dataclass(slots=True)
class DeadlinePayload:
    artifact_hash: str
    title: str
    due_ts: datetime
    tz: str
    confidence: float
    location: Optional[str] = None
    course_code: Optional[str] = None


class Repository:
    """High-level database operations."""

    def __init__(self, session: Session):
        self.session = session

    # Courses -----------------------------------------------------------------
    def get_or_create_course(self, code: str, name: Optional[str] = None, dept: Optional[str] = None) -> Course:
        stmt = select(Course).where(Course.code == code)
        course = self.session.execute(stmt).scalar_one_or_none()
        if course:
            if name and course.name != name:
                course.name = name
            if dept and course.dept != dept:
                course.dept = dept
            return course

        course = Course(code=code, name=name or code, dept=dept)
        self.session.add(course)
        self.session.flush()
        return course

    # Artifacts ---------------------------------------------------------------
    def upsert_artifact(self, data: ArtifactPayload) -> Artifact:
        stmt = select(Artifact).where(Artifact.hash == data.hash)
        artifact = self.session.execute(stmt).scalar_one_or_none()

        if artifact:
            artifact.title = data.title
            artifact.text = data.text
            artifact.url = data.url
            artifact.source = data.source
            artifact.source_loc = data.source_loc
            artifact.published_ts = data.published_ts
            artifact.kind = data.kind
            self._sync_links(artifact, data.links)
            return artifact

        artifact = Artifact(
            kind=data.kind,
            title=data.title,
            text=data.text,
            url=data.url,
            source=data.source,
            source_loc=data.source_loc,
            published_ts=data.published_ts,
            hash=data.hash,
        )
        self.session.add(artifact)
        self.session.flush()
        self._sync_links(artifact, data.links)
        return artifact

    def _sync_links(self, artifact: Artifact, links: Iterable[tuple[str, Optional[str]]]) -> None:
        existing = {(link.href, link.label): link for link in artifact.links}
        desired = {(href, label) for href, label in links}

        # Remove stale links
        for key, link in existing.items():
            if key not in desired:
                self.session.delete(link)

        # Add new links
        for href, label in desired:
            if (href, label) not in existing:
                artifact.links.append(Link(href=href, label=label))

    # Deadlines ---------------------------------------------------------------
    def create_or_update_deadline(self, data: DeadlinePayload) -> Deadline:
        artifact_stmt = select(Artifact).where(Artifact.hash == data.artifact_hash)
        artifact = self.session.execute(artifact_stmt).scalar_one()

        stmt = (
            select(Deadline)
            .where(Deadline.artifact_id == artifact.id)
            .where(Deadline.due_ts == data.due_ts)
            .where(Deadline.title == data.title)
        )
        deadline = self.session.execute(stmt).scalar_one_or_none()

        if deadline:
            deadline.confidence = data.confidence
            deadline.location = data.location
            if data.course_code:
                deadline.course = self.get_or_create_course(data.course_code)
            return deadline

        course = None
        if data.course_code:
            course = self.get_or_create_course(data.course_code)

        deadline = Deadline(
            artifact=artifact,
            title=data.title,
            due_ts=data.due_ts,
            tz=data.tz,
            confidence=data.confidence,
            location=data.location,
        )
        if course:
            deadline.course = course

        self.session.add(deadline)
        return deadline

    def upcoming_deadlines(self, within_days: int, tz: str) -> list[Deadline]:
        now = datetime.now(timezone.utc)
        horizon = now + timedelta(days=within_days)
        stmt = (
            select(Deadline)
            .where(Deadline.status == DeadlineStatus.OPEN)
            .where(Deadline.due_ts >= now)
            .where(Deadline.due_ts <= horizon)
            .order_by(Deadline.due_ts.asc())
        )
        return list(self.session.execute(stmt).scalars())

    def deadlines_next_hours(self, hours: int) -> list[Deadline]:
        now = datetime.now(timezone.utc)
        horizon = now + timedelta(hours=hours)
        stmt = (
            select(Deadline)
            .where(Deadline.status == DeadlineStatus.OPEN)
            .where(Deadline.due_ts >= now)
            .where(Deadline.due_ts <= horizon)
            .order_by(Deadline.due_ts.asc())
        )
        return list(self.session.execute(stmt).scalars())

    def deadlines_today(self, tz: str) -> list[Deadline]:
        # Convert to timezone via SQL functions? For now filter by UTC boundaries.
        now = datetime.now(timezone.utc)
        start = datetime(year=now.year, month=now.month, day=now.day, tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        stmt = (
            select(Deadline)
            .where(Deadline.status == DeadlineStatus.OPEN)
            .where(Deadline.due_ts >= start)
            .where(Deadline.due_ts < end)
            .order_by(Deadline.due_ts.asc())
        )
        return list(self.session.execute(stmt).scalars())

    def update_deadline_status(self, deadline_id: str, status: DeadlineStatus) -> Deadline:
        stmt = select(Deadline).where(Deadline.id == deadline_id)
        deadline = self.session.execute(stmt).scalar_one()
        deadline.status = status
        return deadline

    # Artifacts & metrics -----------------------------------------------------
    def recent_artifacts(self, limit: int = 20) -> list[Artifact]:
        stmt = select(Artifact).order_by(Artifact.discovered_ts.desc()).limit(limit)
        return list(self.session.execute(stmt).scalars())

    # Sync state --------------------------------------------------------------
    def get_sync_cursor(self, source: str) -> Optional[SyncState]:
        stmt = select(SyncState).where(SyncState.source == source)
        return self.session.execute(stmt).scalar_one_or_none()

    def set_sync_cursor(self, source: str, cursor: Optional[str], extra: Optional[str] = None) -> SyncState:
        state = self.get_sync_cursor(source)
        if state:
            state.cursor = cursor
            state.extra = extra
            state.updated_ts = datetime.now(timezone.utc)
            return state

        state = SyncState(source=source, cursor=cursor, extra=extra, updated_ts=datetime.now(timezone.utc))
        self.session.add(state)
        return state

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


def _uuid_str() -> str:
    return str(uuid.uuid4())


class ArtifactKind(str, enum.Enum):
    EMAIL = "email"
    ANNOUNCEMENT = "announcement"
    NOTION = "notion"
    SYLLABUS = "syllabus"
    ASSIGNMENT = "assignment"
    EXAM = "exam"
    POLICY = "policy"


class DeadlineStatus(str, enum.Enum):
    OPEN = "open"
    DONE = "done"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    code: Mapped[str] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(255))
    dept: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    deadlines: Mapped[list["Deadline"]] = relationship(back_populates="course")


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    kind: Mapped[ArtifactKind] = mapped_column(Enum(ArtifactKind, name="artifact_kind"))
    title: Mapped[str] = mapped_column(String(255), index=True)
    text: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(1024), index=True)
    source: Mapped[str] = mapped_column(String(32))
    source_loc: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    published_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    discovered_ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, server_default=func.now()
    )
    hash: Mapped[str] = mapped_column(String(64), unique=True)

    deadlines: Mapped[list["Deadline"]] = relationship(
        back_populates="artifact", cascade="all, delete-orphan"
    )
    links: Mapped[list["Link"]] = relationship(
        back_populates="artifact", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_artifacts_source_hash", "source", "hash", unique=True),)


class Deadline(Base):
    __tablename__ = "deadlines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    course_id: Mapped[Optional[str]] = mapped_column(ForeignKey("courses.id"), index=True)
    artifact_id: Mapped[str] = mapped_column(ForeignKey("artifacts.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    due_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    tz: Mapped[str] = mapped_column(String(64), default="Europe/Istanbul")
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[DeadlineStatus] = mapped_column(
        Enum(DeadlineStatus, name="deadline_status"), default=DeadlineStatus.OPEN
    )

    course: Mapped[Optional[Course]] = relationship(back_populates="deadlines")
    artifact: Mapped["Artifact"] = relationship(back_populates="deadlines")


class Link(Base):
    __tablename__ = "links"

    artifact_id: Mapped[str] = mapped_column(ForeignKey("artifacts.id"), primary_key=True)
    href: Mapped[str] = mapped_column(String(1024), primary_key=True)
    label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    artifact: Mapped[Artifact] = relationship(back_populates="links")


class SyncState(Base):
    __tablename__ = "sync_state"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(64), unique=True)
    cursor: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    extra: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

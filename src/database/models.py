"""
Database models for Ultron
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config.settings import settings

Base = declarative_base()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Announcement(Base):
    """University announcement model"""

    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    date = Column(DateTime)
    link = Column(String)
    notified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ConversationHistory(Base):
    """Chat conversation history"""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    message = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Reminder(Base):
    """Reminders"""

    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    reminder_time = Column(DateTime)
    sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class CourseMaterial(Base):
    """Structured academic content such as chapters, lecture notes, or summaries."""

    __tablename__ = "course_materials"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, index=True, nullable=True)
    title = Column(String, nullable=False)
    chapter = Column(String, nullable=True)
    section = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    tags = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_summary_dict(self, preview_chars: int = 240) -> Dict[str, object]:
        """Return a lightweight representation suitable for search results."""
        body = self.summary or self.content or ""
        preview = body.strip()
        if len(preview) > preview_chars:
            preview = preview[:preview_chars].rstrip() + "..."

        return {
            "id": self.id,
            "course_code": self.course_code,
            "title": self.title,
            "chapter": self.chapter,
            "section": self.section,
            "preview": preview,
            "source_url": self.source_url,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_dict(self) -> Dict[str, object]:
        """Return the full material payload."""
        return {
            "id": self.id,
            "course_code": self.course_code,
            "title": self.title,
            "chapter": self.chapter,
            "section": self.section,
            "summary": self.summary,
            "content": self.content,
            "tags": self.tags,
            "source_url": self.source_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


def init_db():
    """Initialize database"""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")

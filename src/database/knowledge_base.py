"""
Lightweight helper for navigating academic materials stored in the local database.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from loguru import logger
from sqlalchemy import func, or_, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from .models import CourseMaterial, SessionLocal, init_db


class KnowledgeBase:
    """
    Wrapper around SQLAlchemy models that exposes high-level queries for course materials.
    Designed for use by the Ultron agent when it needs to look up chapters, sections, or notes.
    """

    def __init__(self, session_factory=SessionLocal) -> None:
        init_db()
        self._session_factory = session_factory

    def _open_session(self) -> Session:
        return self._session_factory()

    def search_materials(
        self,
        query: Optional[str] = None,
        course_code: Optional[str] = None,
        chapter: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, object]]:
        """
        Search stored materials by keyword with optional course/chapter filters.

        Args:
            query: Text to look for in title, chapter, section, tags, or content.
            course_code: Restrict results to a specific course code (case-insensitive).
            chapter: Restrict to materials whose chapter/section matches this string.
            limit: Maximum number of results to return (clamped to 1..25).
        """
        session = self._open_session()
        limit = max(1, min(limit, 25))
        try:
            stmt = select(CourseMaterial)

            if query:
                norm_query = f"%{query.lower()}%"
                stmt = stmt.where(
                    or_(
                        func.lower(CourseMaterial.title).like(norm_query),
                        func.lower(CourseMaterial.chapter).like(norm_query),
                        func.lower(CourseMaterial.section).like(norm_query),
                        func.lower(CourseMaterial.tags).like(norm_query),
                        func.lower(CourseMaterial.content).like(norm_query),
                    )
                )

            if course_code:
                stmt = stmt.where(func.lower(CourseMaterial.course_code) == course_code.lower())

            if chapter:
                stmt = stmt.where(func.lower(CourseMaterial.chapter).like(f"%{chapter.lower()}%"))

            stmt = (
                stmt.order_by(CourseMaterial.updated_at.desc(), CourseMaterial.created_at.desc())
                .limit(limit)
            )

            materials = session.execute(stmt).scalars().all()
            return [material.to_summary_dict() for material in materials]
        except OperationalError as exc:
            logger.debug("Knowledge base is not initialised yet: %s", exc)
            return []
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to search materials: %s", exc)
            return []
        finally:
            session.close()

    def get_material(self, material_id: int) -> Optional[Dict[str, object]]:
        """Return the full material payload for a given identifier."""
        session = self._open_session()
        try:
            material = session.get(CourseMaterial, material_id)
            return material.to_dict() if material else None
        except OperationalError as exc:
            logger.debug("Knowledge base not available: %s", exc)
            return None
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to load material %s: %s", material_id, exc)
            return None
        finally:
            session.close()

    def list_courses(self) -> List[str]:
        """Return distinct course codes that have stored materials."""
        session = self._open_session()
        try:
            stmt = (
                select(func.distinct(func.lower(CourseMaterial.course_code)))
                .where(CourseMaterial.course_code.isnot(None))
                .order_by(func.lower(CourseMaterial.course_code))
            )
            rows = session.execute(stmt).scalars().all()
            return [row.upper() for row in rows if row]
        except OperationalError as exc:
            logger.debug("Knowledge base not available: %s", exc)
            return []
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to list knowledge base courses: %s", exc)
            return []
        finally:
            session.close()

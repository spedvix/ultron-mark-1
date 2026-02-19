from __future__ import annotations

from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from ..settings import settings


class Base(DeclarativeBase):
    """Base declarative class for all models."""


SessionLocal = sessionmaker(expire_on_commit=False, class_=Session)
_engine: Optional[Engine] = None


def init_engine(database_url: Optional[str] = None) -> Engine:
    """Initialise a SQLAlchemy engine and configure session factory."""
    global _engine
    if _engine is not None:
        return _engine

    database_url = database_url or settings.resolved_database_url
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    _engine = create_engine(
        database_url,
        future=True,
        pool_pre_ping=True,
        connect_args=connect_args,
    )
    SessionLocal.configure(bind=_engine)
    return _engine


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    if _engine is None:
        init_engine()

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

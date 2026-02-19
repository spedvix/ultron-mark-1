from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ultron.connectors.types import AnnouncementItem
from ultron.db.base import Base
from ultron.db.models import Artifact
from ultron.db.repo import Repository
from ultron.extractors.pipeline import ExtractionPipeline


def make_session() -> Session:
    engine = create_engine('sqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)()


def test_announcements_are_deduped_by_hash():
    session = make_session()
    repo = Repository(session)
    pipeline = ExtractionPipeline(repo)
    item = AnnouncementItem(
        source='https://dept.example.edu/announcements',
        title='Campus Closure',
        url='https://dept.example.edu/announcements/closure',
        published_ts=datetime(2025, 10, 20, tzinfo=timezone.utc),
        body='Campus will be closed on 2025-10-25 for maintenance.',
        summary='Campus closed 2025-10-25',
    )

    pipeline.ingest_announcements([item], source='rss')
    pipeline.ingest_announcements([item], source='rss')
    session.commit()

    artifacts = session.query(Artifact).all()
    assert len(artifacts) == 1

    session.close()


from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ultron.connectors.types import EmailMessage
from ultron.db.base import Base
from ultron.db.models import Artifact
from ultron.db.repo import Repository
from ultron.extractors.pipeline import ExtractionPipeline


def make_session() -> Session:
    engine = create_engine('sqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)()


def test_pipeline_creates_artifact_and_deadline():
    session = make_session()
    repo = Repository(session)
    pipeline = ExtractionPipeline(repo, timezone='Europe/Istanbul')
    email = EmailMessage(
        id='1',
        thread_id='thread-1',
        subject='MIS101 HW2 due 2025-11-01 23:59',
        sender='prof@example.edu',
        date=datetime(2025, 10, 20, 8, 0, tzinfo=timezone.utc),
        text='Please submit HW2 by 2025-11-01 23:59 in Room 101.',
        html=None,
        headers={},
    )

    result = pipeline.ingest_emails([email], source='imap')
    session.commit()

    artifacts = session.query(Artifact).all()
    assert len(artifacts) == 1
    assert result.deadlines and result.deadlines[0].course.code == 'MIS101'
    assert result.deadlines[0].due_ts.tzinfo is not None

    session.close()


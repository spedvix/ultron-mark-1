from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ultron.app import create_app
from ultron.api import deps
from ultron.db.base import Base
from ultron.db.repo import ArtifactPayload, DeadlinePayload, Repository
from ultron.db.models import ArtifactKind


def setup_database():
    engine = create_engine(
        'sqlite://',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    return engine, SessionLocal


def seed_data(SessionLocal):
    session = SessionLocal()
    repo = Repository(session)
    published = datetime.now(timezone.utc) - timedelta(hours=1)
    hash_value = 'hash-123'
    repo.upsert_artifact(
        ArtifactPayload(
            kind=ArtifactKind.ASSIGNMENT,
            title='HW2',
            text='Submit by tomorrow',
            url='https://lms.example/hw2',
            source='email',
            source_loc='msg-1',
            published_ts=published,
            hash=hash_value,
            links=[],
        )
    )
    due = datetime.now(timezone.utc) + timedelta(hours=12)
    repo.create_or_update_deadline(
        DeadlinePayload(
            artifact_hash=hash_value,
            title='HW2',
            due_ts=due,
            tz='Europe/Istanbul',
            confidence=0.9,
            location='Room 101',
            course_code='MIS101',
        )
    )
    session.commit()
    session.close()


def test_daily_brief_returns_upcoming_deadline():
    engine, SessionLocal = setup_database()
    seed_data(SessionLocal)

    app = create_app()

    def override_repo():
        session = SessionLocal()
        try:
            yield Repository(session)
        finally:
            session.close()

    app.dependency_overrides[deps.get_repository] = override_repo

    client = TestClient(app)
    response = client.get('/brief/daily?tz=Europe/Istanbul')
    data = response.json()

    assert response.status_code == 200
    assert data['due_next_72h']
    first = data['due_next_72h'][0]
    assert first['course'] == 'MIS101'
    assert first['urgency'] in {'critical', 'warning', 'normal'}
    assert first['due_ts'].startswith('202')

    client.app.dependency_overrides.clear()


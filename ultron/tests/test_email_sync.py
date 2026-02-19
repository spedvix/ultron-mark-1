from dataclasses import dataclass
from datetime import datetime, timezone

from ultron.connectors.email.base import EmailConnector
from ultron.connectors.types import EmailMessage


@dataclass
class State:
    cursor: str | None
    extra: str | None = None


class FakeRepo:
    def __init__(self):
        self.state: State | None = None

    def get_sync_cursor(self, source):
        return self.state

    def set_sync_cursor(self, source, cursor, extra=None):
        self.state = State(cursor=cursor, extra=extra)


class DemoConnector(EmailConnector):
    source_name = 'email:test'

    def __init__(self, messages):
        super().__init__()
        self.messages = messages

    def sync(self, repo):
        cursor = self._get_cursor(repo)
        filtered = []
        highest = cursor
        for msg in self.messages:
            if cursor and int(msg.id) <= int(cursor):
                continue
            if not self.should_keep(msg.subject, msg.text):
                continue
            filtered.append(msg)
            highest = msg.id
        if highest and highest != cursor:
            self._update_cursor(repo, highest)
        return filtered


def make_email(uid, subject, body):
    return EmailMessage(
        id=str(uid),
        thread_id=None,
        subject=subject,
        sender='prof@example.edu',
        date=datetime.now(timezone.utc),
        text=body,
        html=None,
        headers={},
    )


def test_email_connector_filters_keywords_and_updates_cursor():
    repo = FakeRepo()
    connector = DemoConnector(
        [
            make_email(1, 'Welcome', 'General info only'),
            make_email(2, 'Homework reminder', 'assignment due soon'),
            make_email(3, 'Midterm exam', 'exam at 10:00'),
        ]
    )

    first_sync = connector.sync(repo)
    assert len(first_sync) == 2
    assert repo.state and repo.state.cursor == '3'

    connector.messages.append(make_email(4, 'Quiz update', 'quiz moved to Friday'))
    second_sync = connector.sync(repo)
    assert len(second_sync) == 1
    assert second_sync[0].id == '4'
    assert repo.state and repo.state.cursor == '4'


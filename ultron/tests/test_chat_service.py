import types
import pytest

from ultron.services.chat_service import ChatService
from ultron.settings import settings


class _MockUsage:
    total_tokens = 256


class _MockMessage:
    def __init__(self, content: str):
        self.content = content


class _MockChoice:
    def __init__(self, content: str):
        self.message = _MockMessage(content)


class _MockResponse:
    def __init__(self, content: str):
        self.choices = [_MockChoice(content)]
        self.usage = _MockUsage()


@pytest.mark.asyncio
async def test_chat_service_generates_response(monkeypatch):
    settings.openai_api_key = settings.openai_api_key or 'test-key'
    service = ChatService()

    async def _fake_create(**kwargs):
        assert kwargs['model'] == settings.openai_chat_model
        assert kwargs['messages'][0]['role'] == 'system'
        return _MockResponse('Hello from Ultron!')

    monkeypatch.setattr(service._client.chat.completions, 'create', _fake_create)

    reply = await service.generate_reply(
        message='Hi there',
        history=[{'role': 'assistant', 'content': 'Hello!'}],
    )

    assert reply['message'] == 'Hello from Ultron!'
    assert reply['metadata']['model'] == settings.openai_chat_model
    assert reply['metadata']['tokens'] == _MockUsage.total_tokens


@pytest.mark.asyncio
async def test_chat_service_with_attachment(monkeypatch):
    settings.openai_api_key = settings.openai_api_key or 'test-key'
    service = ChatService()

    async def _fake_create(**kwargs):
        user_turn = kwargs['messages'][-1]['content']
        assert 'Attachment:' in user_turn
        return _MockResponse('Attachment acknowledged.')

    monkeypatch.setattr(service._client.chat.completions, 'create', _fake_create)

    attachment = {
        'filename': 'notes.txt',
        'type': 'text',
        'size': 128,
        'content': 'Important lecture notes here.'
    }

    reply = await service.generate_reply(
        message='Please review these notes.',
        attachment=attachment,
    )

    assert 'Attachment acknowledged.' in reply['message']


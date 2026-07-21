import asyncio

from server import protocol
from server.db import init_db, AccountRepository
from server.login import authenticate
from server.protocol import MSG_TYPES


class FakeWebSocket:
    def __init__(self, incoming):
        self._incoming = iter(incoming)
        self.sent = []

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._incoming)
        except StopIteration:
            raise StopAsyncIteration

    async def send(self, message):
        self.sent.append(message)


def make_repo():
    return AccountRepository(init_db(':memory:'))


def test_register_creates_account_and_returns_connection():
    repo = make_repo()
    ws = FakeWebSocket([protocol.encode(MSG_TYPES['REGISTER'], username='efrat', password='secret')])

    conn = asyncio.run(authenticate(ws, repo))

    assert conn.username == 'efrat'
    assert conn.rating == 1200
    assert protocol.decode(ws.sent[-1])['type'] == MSG_TYPES['OK']


def test_login_with_correct_password_succeeds():
    repo = make_repo()
    repo.register('efrat', 'secret')
    ws = FakeWebSocket([protocol.encode(MSG_TYPES['LOGIN'], username='efrat', password='secret')])

    conn = asyncio.run(authenticate(ws, repo))

    assert conn.username == 'efrat'


def test_login_with_wrong_password_fails_and_returns_none():
    repo = make_repo()
    repo.register('efrat', 'secret')
    ws = FakeWebSocket([protocol.encode(MSG_TYPES['LOGIN'], username='efrat', password='wrong')])

    conn = asyncio.run(authenticate(ws, repo))

    assert conn is None
    assert protocol.decode(ws.sent[-1])['type'] == MSG_TYPES['ERROR']


def test_second_attempt_after_failed_login_can_succeed():
    repo = make_repo()
    repo.register('efrat', 'secret')
    ws = FakeWebSocket([
        protocol.encode(MSG_TYPES['LOGIN'], username='efrat', password='wrong'),
        protocol.encode(MSG_TYPES['LOGIN'], username='efrat', password='secret'),
    ])

    conn = asyncio.run(authenticate(ws, repo))

    assert conn.username == 'efrat'


def test_malformed_message_is_skipped_not_fatal():
    repo = make_repo()
    repo.register('efrat', 'secret')
    ws = FakeWebSocket([
        'not json',
        protocol.encode(MSG_TYPES['LOGIN'], username='efrat', password='secret'),
    ])

    conn = asyncio.run(authenticate(ws, repo))

    assert conn.username == 'efrat'


def test_no_messages_returns_none():
    repo = make_repo()
    ws = FakeWebSocket([])

    conn = asyncio.run(authenticate(ws, repo))

    assert conn is None

import asyncio

import protocol
from server.db import AccountRepository
from server.login import authenticate
from protocol import MSG_TYPES


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


def make_repo(db_conn):
    return AccountRepository(db_conn)


def test_register_creates_account_and_returns_connection(db_conn):
    repo = make_repo(db_conn)
    ws = FakeWebSocket([protocol.encode(MSG_TYPES['REGISTER'], username='efrat', password='secret')])

    conn = asyncio.run(authenticate(ws, repo))

    assert conn.username == 'efrat'
    assert conn.rating == 1200
    assert protocol.decode(ws.sent[-1])['type'] == MSG_TYPES['OK']


def test_login_with_correct_password_succeeds(db_conn):
    repo = make_repo(db_conn)
    repo.register('efrat', 'secret')
    ws = FakeWebSocket([protocol.encode(MSG_TYPES['LOGIN'], username='efrat', password='secret')])

    conn = asyncio.run(authenticate(ws, repo))

    assert conn.username == 'efrat'


def test_login_with_wrong_password_fails_and_returns_none(db_conn):
    repo = make_repo(db_conn)
    repo.register('efrat', 'secret')
    ws = FakeWebSocket([protocol.encode(MSG_TYPES['LOGIN'], username='efrat', password='wrong')])

    conn = asyncio.run(authenticate(ws, repo))

    assert conn is None
    assert protocol.decode(ws.sent[-1])['type'] == MSG_TYPES['ERROR']


def test_second_attempt_after_failed_login_can_succeed(db_conn):
    repo = make_repo(db_conn)
    repo.register('efrat', 'secret')
    ws = FakeWebSocket([
        protocol.encode(MSG_TYPES['LOGIN'], username='efrat', password='wrong'),
        protocol.encode(MSG_TYPES['LOGIN'], username='efrat', password='secret'),
    ])

    conn = asyncio.run(authenticate(ws, repo))

    assert conn.username == 'efrat'


def test_malformed_message_is_skipped_not_fatal(db_conn):
    repo = make_repo(db_conn)
    repo.register('efrat', 'secret')
    ws = FakeWebSocket([
        'not json',
        protocol.encode(MSG_TYPES['LOGIN'], username='efrat', password='secret'),
    ])

    conn = asyncio.run(authenticate(ws, repo))

    assert conn.username == 'efrat'


def test_no_messages_returns_none(db_conn):
    repo = make_repo(db_conn)
    ws = FakeWebSocket([])

    conn = asyncio.run(authenticate(ws, repo))

    assert conn is None

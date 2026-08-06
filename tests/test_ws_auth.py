import asyncio

import protocol
from server.persistence.db import AccountRepository
from server.auth.tokens import create_token
from server.auth.ws_auth import authenticate_with_token
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


def test_valid_token_returns_connection(db_conn):
    repo = AccountRepository(db_conn)
    repo.register('efrat', 'secret')
    token = create_token('efrat')
    ws = FakeWebSocket([protocol.encode(MSG_TYPES['AUTHENTICATE'], token=token)])

    conn = asyncio.run(authenticate_with_token(ws, repo))

    assert conn.username == 'efrat'
    assert conn.rating == 1200
    assert protocol.decode(ws.sent[-1])['type'] == MSG_TYPES['OK']


def test_invalid_token_is_rejected(db_conn):
    repo = AccountRepository(db_conn)
    ws = FakeWebSocket([protocol.encode(MSG_TYPES['AUTHENTICATE'], token='not-a-real-token')])

    conn = asyncio.run(authenticate_with_token(ws, repo))

    assert conn is None
    assert protocol.decode(ws.sent[-1])['type'] == MSG_TYPES['ERROR']


def test_token_for_unknown_user_is_rejected(db_conn):
    repo = AccountRepository(db_conn)
    token = create_token('ghost')
    ws = FakeWebSocket([protocol.encode(MSG_TYPES['AUTHENTICATE'], token=token)])

    conn = asyncio.run(authenticate_with_token(ws, repo))

    assert conn is None
    assert protocol.decode(ws.sent[-1])['type'] == MSG_TYPES['ERROR']


def test_retry_after_invalid_token_can_succeed(db_conn):
    repo = AccountRepository(db_conn)
    repo.register('efrat', 'secret')
    good_token = create_token('efrat')
    ws = FakeWebSocket([
        protocol.encode(MSG_TYPES['AUTHENTICATE'], token='bad-token'),
        protocol.encode(MSG_TYPES['AUTHENTICATE'], token=good_token),
    ])

    conn = asyncio.run(authenticate_with_token(ws, repo))

    assert conn.username == 'efrat'


def test_malformed_message_is_skipped_not_fatal(db_conn):
    repo = AccountRepository(db_conn)
    repo.register('efrat', 'secret')
    token = create_token('efrat')
    ws = FakeWebSocket(['not json', protocol.encode(MSG_TYPES['AUTHENTICATE'], token=token)])

    conn = asyncio.run(authenticate_with_token(ws, repo))

    assert conn.username == 'efrat'


def test_non_authenticate_message_is_ignored(db_conn):
    repo = AccountRepository(db_conn)
    repo.register('efrat', 'secret')
    token = create_token('efrat')
    ws = FakeWebSocket([
        protocol.encode(MSG_TYPES['MOVE'], start=[0, 0], end=[0, 1]),
        protocol.encode(MSG_TYPES['AUTHENTICATE'], token=token),
    ])

    conn = asyncio.run(authenticate_with_token(ws, repo))

    assert conn.username == 'efrat'


def test_no_messages_returns_none(db_conn):
    repo = AccountRepository(db_conn)
    ws = FakeWebSocket([])

    conn = asyncio.run(authenticate_with_token(ws, repo))

    assert conn is None

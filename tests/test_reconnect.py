import asyncio

import protocol
from core.config.constants import WHITE_COLOR
from protocol import MSG_TYPES
from server.connection import PlayerConnection
from server.reconnect import try_reconnect
from server.session_manager import SessionManager
from server.tokens import create_ticket


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


def make_active_session():
    sessions = SessionManager()
    white = PlayerConnection(None, 'alice', 1200)
    black = PlayerConnection(None, 'bob', 1200)
    session = sessions.create_session(white, black)
    return sessions, session


def test_reconnect_with_valid_ticket_swaps_in_new_connection():
    sessions, session = make_active_session()
    ticket = create_ticket(session.room_id, 1)
    ws = FakeWebSocket([protocol.encode(MSG_TYPES['RECONNECT'], ticket=ticket)])
    new_conn = PlayerConnection(ws, 'alice', 1200)

    result = asyncio.run(try_reconnect(ws, new_conn, sessions))

    assert result is session
    assert session.players[WHITE_COLOR] is new_conn


def test_reconnect_rejects_invalid_ticket_but_keeps_listening():
    sessions, session = make_active_session()
    good_ticket = create_ticket(session.room_id, 1)
    ws = FakeWebSocket([
        protocol.encode(MSG_TYPES['RECONNECT'], ticket='not-a-real-ticket'),
        protocol.encode(MSG_TYPES['RECONNECT'], ticket=good_ticket),
    ])
    new_conn = PlayerConnection(ws, 'alice', 1200)

    result = asyncio.run(try_reconnect(ws, new_conn, sessions))

    assert result is session


def test_reconnect_to_nonexistent_room_fails_cleanly():
    sessions = SessionManager()
    ticket = create_ticket('ghost-room', 1)
    ws = FakeWebSocket([protocol.encode(MSG_TYPES['RECONNECT'], ticket=ticket)])
    conn = PlayerConnection(ws, 'alice', 1200)

    result = asyncio.run(try_reconnect(ws, conn, sessions))

    assert result is None
    assert protocol.decode(ws.sent[-1])['message'] == 'room no longer active'


def test_reconnect_username_not_in_room_is_rejected():
    sessions, session = make_active_session()
    ticket = create_ticket(session.room_id, 1)
    ws = FakeWebSocket([protocol.encode(MSG_TYPES['RECONNECT'], ticket=ticket)])
    stranger = PlayerConnection(ws, 'mallory', 1200)

    result = asyncio.run(try_reconnect(ws, stranger, sessions))

    assert result is None


def test_non_reconnect_message_is_ignored():
    sessions, session = make_active_session()
    ticket = create_ticket(session.room_id, 1)
    ws = FakeWebSocket([
        protocol.encode(MSG_TYPES['MOVE'], start=[0, 0], end=[0, 1]),
        protocol.encode(MSG_TYPES['RECONNECT'], ticket=ticket),
    ])
    new_conn = PlayerConnection(ws, 'alice', 1200)

    result = asyncio.run(try_reconnect(ws, new_conn, sessions))

    assert result is session


def test_no_messages_returns_none():
    sessions, session = make_active_session()
    ws = FakeWebSocket([])
    conn = PlayerConnection(ws, 'alice', 1200)

    result = asyncio.run(try_reconnect(ws, conn, sessions))

    assert result is None

import asyncio

from core.config.constants import WHITE_COLOR, BLACK_COLOR
from server.connection import PlayerConnection
from protocol import GameOver, PieceSnapshot
from server.session import GameSession


class FakeWebSocket:
    def __init__(self):
        self.sent = []

    async def send(self, message):
        self.sent.append(message)


class FailingWebSocket:
    async def send(self, message):
        raise ConnectionError('connection closed')


def make_session():
    white = PlayerConnection(None, 'alice', 1200)
    black = PlayerConnection(None, 'bob', 1200)
    session = GameSession('room1', white, black)
    return session, white, black


def test_players_get_room_id_assigned():
    session, white, black = make_session()
    assert white.room_id == 'room1'
    assert black.room_id == 'room1'


def test_connections_includes_both_players_and_no_viewers_by_default():
    session, white, black = make_session()
    assert session.connections() == [white, black]


def test_color_of_identifies_each_player():
    session, white, black = make_session()
    assert session.color_of(white) == WHITE_COLOR
    assert session.color_of(black) == BLACK_COLOR


def test_color_of_unknown_connection_is_none():
    session, _, _ = make_session()
    stranger = PlayerConnection(None, 'mallory', 1200)
    assert session.color_of(stranger) is None


def test_white_can_move_own_pawn():
    session, white, _ = make_session()
    assert session.try_move(white, (6, 0), (5, 0)) is True


def test_black_cannot_move_whites_pawn():
    session, _, black = make_session()
    assert session.try_move(black, (6, 0), (5, 0)) is False
    assert session.state.movements == []


def test_unknown_connection_cannot_move():
    session, _, _ = make_session()
    stranger = PlayerConnection(None, 'mallory', 1200)
    assert session.try_move(stranger, (6, 0), (5, 0)) is False


def test_white_can_jump_own_king():
    session, white, _ = make_session()
    assert session.try_jump(white, 7, 4) is True


def test_black_cannot_jump_whites_king():
    session, _, black = make_session()
    assert session.try_jump(black, 7, 4) is False
    assert session.state.jumps == []


def test_next_broadcast_returns_event_from_legal_action():
    session, white, _ = make_session()
    session.try_jump(white, 7, 4)
    message = asyncio.run(session.next_broadcast())
    assert message.event == 'jump_started'


def test_end_wakes_up_a_pending_next_broadcast_with_none():
    session, _, _ = make_session()
    session.end('finished')
    assert asyncio.run(session.next_broadcast()) is None


def test_snapshot_includes_all_32_starting_pieces():
    session, _, _ = make_session()
    snapshot = session.snapshot()
    assert len(snapshot.pieces) == 32


def test_snapshot_omits_empty_cells():
    session, _, _ = make_session()
    snapshot = session.snapshot()
    assert '4,4' not in snapshot.pieces


def test_snapshot_reports_idle_piece_identity_and_state():
    session, _, _ = make_session()
    snapshot = session.snapshot()
    assert snapshot.pieces['6,0'] == PieceSnapshot(piece='wP', state='idle')


def test_snapshot_includes_start_end_progress_for_moving_piece():
    session, white, _ = make_session()
    session.try_move(white, (6, 0), (4, 0))

    snapshot = session.snapshot()

    entry = snapshot.pieces['6,0']
    assert entry.state == 'move'
    assert entry.start == [6, 0]
    assert entry.end == [4, 0]
    assert 0 <= entry.progress <= 1


def test_snapshot_jumping_piece_has_no_start_end_progress():
    session, white, _ = make_session()
    session.try_jump(white, 7, 4)

    snapshot = session.snapshot()

    entry = snapshot.pieces['7,4']
    assert entry.state == 'jump'
    assert entry.start is None
    assert entry.end is None
    assert entry.progress is None


def test_snapshot_includes_scores_and_game_over_flag():
    session, _, _ = make_session()
    snapshot = session.snapshot()
    assert snapshot.scores == {WHITE_COLOR: 0, BLACK_COLOR: 0}
    assert snapshot.game_over is False


def test_broadcast_sends_message_to_both_players():
    white_ws, black_ws = FakeWebSocket(), FakeWebSocket()
    white = PlayerConnection(white_ws, 'alice', 1200)
    black = PlayerConnection(black_ws, 'bob', 1200)
    session = GameSession('room1', white, black)

    asyncio.run(session.broadcast(GameOver(winner=WHITE_COLOR, time=0)))

    assert len(white_ws.sent) == 1
    assert len(black_ws.sent) == 1


def test_broadcast_survives_one_failed_connection():
    white = PlayerConnection(FailingWebSocket(), 'alice', 1200)
    black_ws = FakeWebSocket()
    black = PlayerConnection(black_ws, 'bob', 1200)
    session = GameSession('room1', white, black)

    asyncio.run(session.broadcast(GameOver(winner=WHITE_COLOR, time=0)))

    assert len(black_ws.sent) == 1

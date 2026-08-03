import asyncio

from core.config.constants import WHITE_COLOR, BLACK_COLOR
from protocol import PieceSnapshot, Snapshot
from server.recovery import recover_room
from server.room_state import ROOM_OWNER_KEY, RoomState
from server.session_manager import SessionManager


class FakeRepo:
    def __init__(self, ratings):
        self.ratings = ratings

    def get_rating(self, username):
        return self.ratings.get(username)


def test_recover_room_rebuilds_board_and_pauses_both_players(redis_client):
    store = RoomState(redis_client)
    snapshot = Snapshot(
        pieces={
            '6,0': PieceSnapshot(piece='wP', state='idle'),
            '1,0': PieceSnapshot(piece='bP', state='idle'),
        },
        scores={'w': 3, 'b': 1},
        game_over=False,
    )
    sessions = SessionManager()
    repo = FakeRepo({'alice': 1250, 'bob': 1180})

    async def scenario():
        await store.save_snapshot('room1', snapshot)
        await store.save_players('room1', 'alice', 'bob')
        return await recover_room('room1', store, repo, sessions, 'shard-a')

    session = asyncio.run(scenario())

    assert session is not None
    assert session.room_id == 'room1'
    assert session.players[WHITE_COLOR].username == 'alice'
    assert session.players[WHITE_COLOR].rating == 1250
    assert session.players[BLACK_COLOR].username == 'bob'
    assert session.players[BLACK_COLOR].rating == 1180
    assert session.board.get_piece_str(6, 0) == 'wP'
    assert session.board.get_piece_str(1, 0) == 'bP'
    assert session.state.scores == {'w': 3, 'b': 1}
    assert session.is_paused() is True
    assert sessions.get('room1') is session


def test_recover_room_returns_none_when_snapshot_missing(redis_client):
    store = RoomState(redis_client)
    sessions = SessionManager()
    repo = FakeRepo({})

    async def scenario():
        await store.save_players('room1', 'alice', 'bob')
        return await recover_room('room1', store, repo, sessions, 'shard-a')

    assert asyncio.run(scenario()) is None


def test_recover_room_returns_none_when_players_missing(redis_client):
    store = RoomState(redis_client)
    sessions = SessionManager()
    repo = FakeRepo({})
    snapshot = Snapshot(pieces={}, scores={'w': 0, 'b': 0}, game_over=False)

    async def scenario():
        await store.save_snapshot('room1', snapshot)
        return await recover_room('room1', store, repo, sessions, 'shard-a')

    assert asyncio.run(scenario()) is None


def test_recover_room_bumps_epoch_via_claim(redis_client):
    store = RoomState(redis_client)
    sessions = SessionManager()
    repo = FakeRepo({'alice': 1200, 'bob': 1200})
    snapshot = Snapshot(pieces={}, scores={'w': 0, 'b': 0}, game_over=False)

    async def scenario():
        await store.claim_room('room1', 'old-shard')
        await store.save_snapshot('room1', snapshot)
        await store.save_players('room1', 'alice', 'bob')
        await redis_client.delete(ROOM_OWNER_KEY.format(room_id='room1'))

        await recover_room('room1', store, repo, sessions, 'new-shard')
        return await store.get_epoch('room1')

    assert asyncio.run(scenario()) == 2

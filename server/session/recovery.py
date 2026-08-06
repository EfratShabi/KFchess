from core.config.constants import EMPTY_CELL
from core.domain.board import Board
from server.session.connection import PlayerConnection
from server.session.session import GameSession

BOARD_SIZE = 8


def _build_board(snapshot, size=BOARD_SIZE):
    grid = [[EMPTY_CELL] * size for _ in range(size)]
    for key, piece in snapshot.pieces.items():
        row, col = map(int, key.split(','))
        grid[row][col] = piece.piece
    return Board(grid)


async def recover_room(room_id, room_state, repo, sessions, shard_id):
    snapshot = await room_state.get_snapshot(room_id)
    players = await room_state.get_players(room_id)
    if snapshot is None or players is None:
        await room_state.clear_room(room_id)
        return None
    white_username, black_username = players

    board = _build_board(snapshot)
    white_conn = PlayerConnection(None, white_username, repo.get_rating(white_username))
    black_conn = PlayerConnection(None, black_username, repo.get_rating(black_username))
    session = GameSession(room_id, white_conn, black_conn, board=board)
    session.state.scores = snapshot.scores
    session.mark_disconnected(white_conn)
    session.mark_disconnected(black_conn)

    await room_state.claim_room(room_id, shard_id)
    sessions.restore(session)
    return session

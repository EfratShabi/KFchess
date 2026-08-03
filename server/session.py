import time
from enum import Enum

from core.config.constants import WHITE_COLOR, BLACK_COLOR
from core.domain.board_factory import create_standard_board
from core.real_time.real_time import RealTime
from core.services.game_service import GameService
from server.broadcaster import NetworkBroadcaster
from server.logging_config import get_logger
from protocol import PieceSnapshot, Snapshot

RECONNECT_GRACE_SECONDS = 20


class SessionStatus(Enum):
    ACTIVE = 'active'
    FINISHED = 'finished'
    DISCONNECTED = 'disconnected'


class GameSession:
    def __init__(self, room_id, white_conn, black_conn, board=None):
        self.room_id = room_id
        self.board = board if board is not None else create_standard_board()
        self.state = RealTime()
        self.service = GameService(self.board, self.state)
        self.broadcaster = NetworkBroadcaster()
        self.state.add_observer(self.broadcaster)

        self.players = {WHITE_COLOR: white_conn, BLACK_COLOR: black_conn}
        self.viewers = []
        self.status = SessionStatus.ACTIVE
        self.disconnect_deadlines = {}

        white_conn.room_id = room_id
        black_conn.room_id = room_id

    def connections(self):
        return list(self.players.values()) + self.viewers

    def color_of(self, conn):
        for color, player_conn in self.players.items():
            if player_conn is conn:
                return color
        return None

    def color_of_username(self, username):
        for color, conn in self.players.items():
            if conn.username == username:
                return color
        return None

    def mark_disconnected(self, conn):
        color = self.color_of(conn)
        self.disconnect_deadlines[color] = time.monotonic() + RECONNECT_GRACE_SECONDS

    def mark_reconnected(self, color, new_conn):
        self.players[color] = new_conn
        new_conn.room_id = self.room_id
        self.disconnect_deadlines.pop(color, None)

    def is_paused(self):
        return bool(self.disconnect_deadlines)

    def expired_disconnects(self):
        now = time.monotonic()
        return [color for color, deadline in self.disconnect_deadlines.items() if now >= deadline]

    def try_move(self, conn, start, end):
        color = self.color_of(conn)
        if color is None or self.board.get_piece_color(*start) != color:
            return False
        return self.service.try_move(start, end)

    def try_jump(self, conn, row, col):
        color = self.color_of(conn)
        if color is None or self.board.get_piece_color(row, col) != color:
            return False
        return self.service.try_jump(row, col)

    async def next_broadcast(self):
        return await self.broadcaster.queue.get()

    def end(self, status):
        self.status = status
        self.broadcaster.queue.put_nowait(None)

    async def broadcast(self, message):
        for conn in self.connections():
            try:
                await conn.send(message)
            except Exception:
                get_logger().warning(f'failed to send to {conn.username} in room {self.room_id}')

    def snapshot(self):
        pieces = {}
        for row in range(self.board.rows):
            for col in range(self.board.cols):
                if self.board.is_empty(row, col):
                    continue
                state_name, _ = self.service.get_piece_state(row, col)
                piece_snapshot = PieceSnapshot(piece=self.board.get_piece_str(row, col), state=state_name)
                movement = self.service.get_piece_movement(row, col)
                if movement is not None:
                    start, end, progress = movement
                    piece_snapshot.start = list(start)
                    piece_snapshot.end = list(end)
                    piece_snapshot.progress = progress
                pieces[f'{row},{col}'] = piece_snapshot

        return Snapshot(
            pieces=pieces,
            scores=self.service.get_scores(),
            game_over=self.service.is_game_over(),
        )

from core.config.constants import WHITE_COLOR, BLACK_COLOR
from core.domain.board_factory import create_standard_board
from core.real_time.real_time import RealTime
from core.services.game_service import GameService
from server.broadcaster import NetworkBroadcaster
from server.protocol import MSG_TYPES


class GameSession:
    def __init__(self, room_id, white_conn, black_conn):
        self.room_id = room_id
        self.board = create_standard_board()
        self.state = RealTime()
        self.service = GameService(self.board, self.state)
        self.broadcaster = NetworkBroadcaster()
        self.state.add_observer(self.broadcaster)

        self.players = {WHITE_COLOR: white_conn, BLACK_COLOR: black_conn}
        self.viewers = []
        self.status = 'active'

        white_conn.room_id = room_id
        black_conn.room_id = room_id

    def connections(self):
        return list(self.players.values()) + self.viewers

    def color_of(self, conn):
        for color, player_conn in self.players.items():
            if player_conn is conn:
                return color
        return None

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

    def pull_outbox(self):
        return self.broadcaster.drain()

    async def broadcast(self, message):
        for conn in self.connections():
            await conn.send(message)

    def snapshot(self):
        pieces = {}
        for row in range(self.board.rows):
            for col in range(self.board.cols):
                if self.board.is_empty(row, col):
                    continue
                state_name, _ = self.service.get_piece_state(row, col)
                entry = {'piece': self.board.get_piece_str(row, col), 'state': state_name}
                movement = self.service.get_piece_movement(row, col)
                if movement is not None:
                    start, end, progress = movement
                    entry['start'] = list(start)
                    entry['end'] = list(end)
                    entry['progress'] = progress
                pieces[f'{row},{col}'] = entry

        return {
            'type': MSG_TYPES['STATE_UPDATE'],
            'event': 'snapshot',
            'pieces': pieces,
            'scores': self.service.get_scores(),
            'game_over': self.service.is_game_over(),
        }

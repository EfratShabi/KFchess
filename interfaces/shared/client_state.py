import time as time_module

from core.config.constants import MS_PER_CELL, WHITE_COLOR, BLACK_COLOR, EMPTY_CELL
from core.domain.board_factory import create_standard_board
from core.domain.movement import Movement
from core.domain.position import Position
from core.domain.time_span import TimeSpan


def _now_ms():
    return int(time_module.monotonic() * 1000)


class ClientGameState:
    """Render-only local mirror of a live match, built entirely from server messages."""

    def __init__(self):
        self.board = create_standard_board()
        self.scores = {WHITE_COLOR: 0, BLACK_COLOR: 0}
        self.game_over = False
        self.event_log = []
        self._movements = {}    # start (row, col) -> Movement
        self._state_names = {}  # (row, col) -> state name
        self._entered_at = {}   # (row, col) -> local ms timestamp the state last changed

    # ---------- contract BoardRenderer already expects (same shape as GameService) ----------

    def get_board_grid(self):
        return self.board.grid

    def get_piece_state(self, row, col):
        if self.board.is_empty(row, col):
            return None
        state_name = self._state_names.get((row, col), 'idle')
        entered_at = self._entered_at.get((row, col), _now_ms())
        return state_name, TimeSpan(entered_at, _now_ms())

    def get_piece_movement(self, row, col):
        movement = self._movements.get((row, col))
        if movement is None:
            return None
        return movement.start, movement.end, movement.progress(_now_ms())

    def get_scores(self):
        return self.scores

    def get_event_log(self):
        return self.event_log

    def is_game_over(self):
        return self.game_over

    # ---------- applying incoming server messages ----------

    def apply_snapshot(self, snapshot):
        grid = [[EMPTY_CELL] * self.board.cols for _ in range(self.board.rows)]
        self._movements.clear()
        for key, piece in snapshot.pieces.items():
            row, col = (int(part) for part in key.split(','))
            grid[row][col] = piece.piece
            self._set_state(row, col, piece.state)
            if piece.start is not None:
                self._track_movement(piece.piece, tuple(piece.start), tuple(piece.end), piece.progress)
        self.board.grid = grid
        self.scores = snapshot.scores
        self.game_over = snapshot.game_over

    def apply_event(self, event):
        handler = getattr(self, f'_handle_{type(event).__name__}', None)
        if handler is not None:
            handler(event)




    def _handle_MoveStarted(self, event):
        start, end = tuple(event.start), tuple(event.end)
        self._set_state(*start, 'move')
        self._track_movement(event.piece, start, end, progress=0.0)
        self.event_log.append(f'{event.piece} {start} -> {end}')

    def _handle_JumpStarted(self, event):
        cell = tuple(event.cell)
        self._set_state(*cell, 'jump')
        self.event_log.append(f'{event.piece} jumps at {cell}')

    def _handle_MoveLanded(self, event):
        end = tuple(event.end)
        start = self._pop_movement_by_end(event.piece, end)
        if start is not None:
            self.board.set_piece(*end, event.piece)
            self.board.clear_cell(*start)
        self._set_state(*end, event.next_state)
        self.event_log.append(f'{event.piece} landed at {end}')

    def _handle_JumpLanded(self, event):
        cell = tuple(event.cell)
        self._set_state(*cell, event.next_state)
        self.event_log.append(f'{event.piece} finished jump at {cell}')

    def _handle_MoveCaptured(self, event):
        position = tuple(event.position)
        start = self._pop_movement_by_end(event.attacker, position)
        if start is not None:
            self.board.clear_cell(*start)
        self.board.set_piece(*position, event.attacker)
        self._set_state(*position, 'idle')
        self.event_log.append(f'{event.attacker} captured {event.captured} at {position}')

    def _handle_MidairCapture(self, event):
        position = tuple(event.position)
        start = self._pop_movement_by_end(event.captured, position)
        if start is not None:
            self.board.clear_cell(*start)
            self._set_state(*start, 'idle')
        self.event_log.append(f'{event.attacker} intercepted {event.captured} mid-air at {position}')

    def _handle_ErrorMessage(self, event):
        self.event_log.append(f'error: {event.message}')

    def _handle_GameOver(self, event):
        self.game_over = True
        self.event_log.append(f'game over — winner: {event.winner}')

    # ---------- small internal helpers ----------

    def _set_state(self, row, col, state_name):
        key = (row, col)
        if self._state_names.get(key) != state_name:
            self._entered_at[key] = _now_ms()
        self._state_names[key] = state_name

    def _track_movement(self, piece, start, end, progress):
        distance = Position.distance(start, end)
        duration_ms = distance * MS_PER_CELL
        elapsed_ms = progress * duration_ms
        started_at = _now_ms() - elapsed_ms
        self._movements[start] = Movement(piece, start, end, started_at, started_at + duration_ms)

    def _pop_movement_by_end(self, piece, end):
        for start, movement in list(self._movements.items()):
            if movement.piece == piece and movement.end == end:
                del self._movements[start]
                return start
        return None

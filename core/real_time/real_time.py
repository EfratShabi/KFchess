from core.config.constants import MS_PER_CELL, JUMP_DURATION_MS, KING, MOVE_COOLDOWN_MS, JUMP_COOLDOWN_MS
from core.domain.movement import Movement
from core.domain.jump import Jump
from core.domain.rest import Rest
from core.domain.position import Position
from core.domain.state_registry import STATE_REGISTRY
from core.real_time.piece_state_tracker import PieceStateTracker


class RealTime:
    def __init__(self):
        self.current_time = 0
        self.game_over = False

        self.movements = []
        self.jumps = []
        self.rests = []
        self.tracker = PieceStateTracker(STATE_REGISTRY)

    def init_piece_states(self, board):
        for row in range(board.rows):
            for col in range(board.cols):
                if not board.is_empty(row, col):
                    self.tracker.set_state(Position(row, col), "idle", self.current_time)

    def is_moving(self, row, col):
        return any(m.start == Position(row, col) for m in self.movements)

    def get_movement(self, row, col):
        return next((m for m in self.movements if m.start == Position(row, col)), None)

    def is_jumping(self, row, col):
        return any(j.cell == Position(row, col) for j in self.jumps)

    def is_resting(self, row, col):
        return any(r.position == Position(row, col) and r.is_ongoing_cooldown(self.current_time) for r in self.rests)

    def advance_time(self, ms):
        self.current_time += ms

    def register_move(self, start, end, piece, distance):
        duration = distance * MS_PER_CELL
        start_time = self.current_time
        arrival_time = self.current_time + duration
        self.movements.append(Movement(piece, start, end, start_time, arrival_time))
        self.tracker.set_state(start, "move", self.current_time)

    def register_jump(self, cell, piece):
        arrival_time = self.current_time + JUMP_DURATION_MS
        self.jumps.append(Jump(piece, cell, arrival_time))
        self.tracker.set_state(cell, "jump", self.current_time)

    def _register_rest(self, position, piece, duration_ms):
        ready_at = self.current_time + duration_ms
        self.rests.append(Rest(piece, position, ready_at))

    def update(self, board):
        if self.game_over:
            return
        due_movements = [m for m in self.movements if m.is_due(self.current_time)]
        for movement in due_movements:
            self._resolve_movement(movement, board)
            self.movements.remove(movement)
        due_jumps = [j for j in self.jumps if self.current_time >= j.arrival_time]
        for jump in due_jumps:
            board.set_piece(jump.cell.row, jump.cell.col, jump.piece)
            self._register_rest(jump.cell, jump.piece, JUMP_COOLDOWN_MS)
            self.jumps.remove(jump)
        self.rests = [r for r in self.rests if r.is_ongoing_cooldown(self.current_time)]
        self.tracker.advance(self.current_time)


    def _resolve_movement(self, movement, board):
        landing_jump = next((j for j in self.jumps if j.intercepts(movement)), None)
        if landing_jump is not None:
            self._capture_midair(landing_jump, movement, board)
            return
        self._land_move(movement, board)

    def _capture_midair(self, jump, movement, board):
        self.jumps.remove(jump) 
        board.clear_cell(*movement.start)  

        if movement.piece[1] == KING:
            self.game_over = True
            print("The King was captured in mid-air! Game Over.")



    def _land_move(self, movement, board):
        target = board.get_piece_str(*movement.end)
        if target and target[1] == KING:
            self.game_over = True
            print("The King was captured! Game Over.")
        board.set_piece(*movement.end, movement.piece)
        board.clear_cell(*movement.start)
        self._register_rest(movement.end, movement.piece, MOVE_COOLDOWN_MS)
        next_state = self.tracker.get_state(movement.start).spec.next_state_when_finished
        self.tracker.move_state(movement.start, movement.end)
        self.tracker.set_state(movement.end, next_state, self.current_time)



from core.real_time.real_time import RealTime
from core.domain.movement_rules import MovementRules
from core.domain.position import Position
from core.domain.time_span import TimeSpan


class GameService:
    def __init__(self, board, state: RealTime):
        self.board = board
        self.state = state
        self.rules = MovementRules()
        self.state.init_piece_states(self.board) #אתחול מצבים לכלים בתחילת המשחק

    def process_wait(self, duration):
        if self.state.game_over:
            return
        self.state.advance_time(duration)
        self.state.update(self.board)

    def get_board_string(self):
        return str(self.board)

    def get_board_grid(self):
        return self.board.grid
    
    #מחזירה טאפל של (שם המצב, פרק הזמן שבו הוא נכנס למצב + הזמן הנוכחי)
    def get_piece_state(self, row, col):
        active = self.state.tracker.get_state(Position(row, col))
        if active is None:
            return None
        return active.spec.name, TimeSpan(active.entered_at, self.state.current_time)


    def get_piece_movement(self, row, col):
        movement = self.state.get_movement(row, col)
        if movement is None:
            return None
        return movement.start, movement.end, movement.progress(self.state.current_time)

    def is_game_over(self):
        return self.state.game_over

    def get_scores(self):
        return self.state.scores

    def try_jump(self, row, col):
        if not self.board.is_in_bounds(row, col):
            return False
        if self.board.is_empty(row, col):
            return False
        if self._is_busy(row, col):
            return False
        piece_str = self.board.get_piece_str(row, col)
        self.state.register_jump(Position(row, col), piece_str)
        return True

    def try_move(self, start, end):
        if self._is_busy(*start):
            return False
        piece_str = self.board.get_piece_str(*start)
        if not self.rules.is_valid_move(self.board.grid, piece_str, start, end):
            return False
        distance = Position.distance(start, end)
        self.state.register_move(start, end, piece_str, distance)
        return True

    def _is_busy(self, row, col):
        state = self.state.tracker.get_state(Position(row, col))
        return state is not None and state.spec.name != "idle"

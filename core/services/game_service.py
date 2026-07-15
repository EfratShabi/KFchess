from core.real_time.real_time import RealTime
from core.domain.movement_rules import MovementRules
from core.domain.position import Position


class GameService:
    def __init__(self, board, state: RealTime):
        self.board = board
        self.state = state
        self.rules = MovementRules()

    def process_wait(self, duration):
        if self.state.game_over:
            return
        self.state.advance_time(duration)
        self.state.update(self.board)

    def get_board_string(self):
        return str(self.board)

    def get_board_grid(self):
        return self.board.grid

    def is_game_over(self):
        return self.state.game_over

    def try_jump(self, row, col):
        if not self.board.is_in_bounds(row, col):
            return False
        if self.board.is_empty(row, col):
            return False
        if self.state.is_moving(row, col) or self.state.is_jumping(row, col):
            return False
        piece_str = self.board.get_piece_str(row, col)
        self.state.register_jump(Position(row, col), piece_str)
        return True

    def try_move(self, start, end):
        piece_str = self.board.get_piece_str(*start)
        if not self.rules.is_valid_move(self.board.grid, piece_str, start, end):
            return False
        distance = self.rules.calc_distance(start, end)
        self.state.register_move(start, end, piece_str, distance)
        return True

from adapters.board_mapper import pixel_to_cell
from real_time.real_time import RealTime
from domain.movement_rules import MovementRules
from domain.position import Position


class GameService:
    def __init__(self, board, state: RealTime):
        self.board = board
        self.state = state
        self.selected_piece = None
        self.rules = MovementRules()
    
    def process_wait(self, duration):
        self.state.advance_time(duration)
        self.state.update(self.board)


    def get_board_string(self):
        return str(self.board)

    def is_game_over(self):
        return self.state.game_over
    
    def _resolve_cell(self, x, y):
        pos = Position(*pixel_to_cell(x, y))
        if not self.board.is_in_bounds(pos.row, pos.col):
            return None
        if self.state.is_moving(pos.row, pos.col) or self.state.is_jumping(pos.row, pos.col):
            return None
        return pos


    def process_click(self, x, y):
        pos = Position(*pixel_to_cell(x, y))
        if not self.board.is_in_bounds(pos.row, pos.col):
            return
        if self.state.is_moving(pos.row, pos.col) or self.state.is_jumping(pos.row, pos.col):
           return
        if self.selected_piece is None:
            self._select_piece(pos)
        else:
            self._try_move(pos)


    def process_jump(self, x, y):
        pos = Position(*pixel_to_cell(x, y))
        if not self.board.is_in_bounds(pos.row, pos.col):
            return
        if self.board.is_empty(pos.row, pos.col):
            return
        if self.state.is_moving(pos.row, pos.col) or self.state.is_jumping(pos.row, pos.col):
            return

        piece_str = self.board.get_piece_str(pos.row, pos.col)
        self.state.register_jump(pos.as_tuple(), piece_str)


    def _select_piece(self, pos):
        if not self.board.is_empty(pos.row, pos.col):
            self.selected_piece = pos


    def _try_move(self, pos):
        prev = self.selected_piece
        piece_str = self.board.get_piece_str(prev.row, prev.col)

        if not self.board.is_empty(pos.row, pos.col):
            if self.board.get_piece_color(pos.row, pos.col) == piece_str[0]:
                self.selected_piece = pos
                return

        if self.rules.is_valid_move(self.board.grid, piece_str, prev.as_tuple(), pos.as_tuple()):
            distance = self.rules.calc_distance(prev.as_tuple(), pos.as_tuple())
            self.state.register_move(prev.as_tuple(), pos.as_tuple(), piece_str, distance)
        self.selected_piece = None


    
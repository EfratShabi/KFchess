from domain.piece import create_piece
from adapters.board_mapper import pixel_to_cell

class GameService:
    def __init__(self, board, arbiter):
        self.board = board
        self.arbiter = arbiter
        self.selected_piece = None
    
    def process_wait(self, duration):
        self.arbiter.advance_time(duration)
        self.arbiter.update(self.board)

    def get_board_string(self):
        return str(self.board)


    def process_click(self, x, y):
        row, col = pixel_to_cell(x, y)

        if not self.board.is_in_bounds(row, col):
            return
        if self.arbiter.is_moving(row, col):
            return

        if self.selected_piece is None:
            self._select_piece(row, col)
        else:
            self._try_move(row, col)
        

    def _select_piece(self, row, col):
        if not self.board.is_empty(row, col):
            self.selected_piece = (row, col)
    

    
    def _try_move(self, row, col):
        prev_row, prev_col = self.selected_piece
        piece_str = self.board.get_piece_str(prev_row, prev_col)

        if not self.board.is_empty(row, col):
            if self.board.get_piece_color(row, col) == piece_str[0]:
                self.selected_piece = (row, col)
                return

        piece = create_piece(piece_str)
        if piece.can_move(self.board.grid, (prev_row, prev_col), (row, col)):
            distance = max(abs(row - prev_row), abs(col - prev_col))
            self.arbiter.register_move((prev_row, prev_col), (row, col), piece_str, distance)
            self.selected_piece = None


    
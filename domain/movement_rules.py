from domain.board import EMPTY_CELL
from domain.piece import create_piece


class MovementRules:
#בדיקות על התנועה-ולידציה
    def is_valid_move(self, board, piece_str, start, end):
        if self._is_same_cell(start, end):
            return False
        if self._is_friendly_fire(board, piece_str, end):
            return False
        piece = create_piece(piece_str)
        return piece.validate_move_by_piece_rules(board, start, end)


    def _is_same_cell(self, start, end):
        """הכלי לא יכול לנוע לאותו תא שבו הוא כבר נמצא."""
        return start == end

    def _is_friendly_fire(self, board, piece_str, end):
        target = board[end.row][end.col]
        return target != EMPTY_CELL and target[0] == piece_str[0]

    def _is_path_clear(self, board, start, end):
        sr, sc = start.row, start.col
        er, ec = end.row, end.col
        row_step = 0 if sr == er else (1 if er > sr else -1)
        col_step = 0 if sc == ec else (1 if ec > sc else -1)
        r, c = sr + row_step, sc + col_step
        while (r, c) != (er, ec):
            if board[r][c] != EMPTY_CELL:
                return False
            r += row_step
            c += col_step
        return True

    def calc_distance(self, start, end):
        return max(abs(end.row - start.row), abs(end.col - start.col))

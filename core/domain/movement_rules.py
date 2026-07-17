from core.domain.board import EMPTY_CELL
from core.domain.piece import create_piece


class MovementRules:
    def is_valid_move(self, board, piece_str, start, end):
        if self._is_same_cell(start, end):
            return False
        if self._is_friendly_fire(board, piece_str, end):
            return False
        piece = create_piece(piece_str)
        return piece.can_move(board, start, end)


    def _is_same_cell(self, start, end):
        return start == end

    def _is_friendly_fire(self, board, piece_str, end):
        er, ec = end
        target = board[er][ec]
        return target != EMPTY_CELL and target[0] == piece_str[0]

    def calc_distance(self, start, end):
        return max(abs(end[0] - start[0]), abs(end[1] - start[1]))

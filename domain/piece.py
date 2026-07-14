from domain.board import EMPTY_CELL

class Piece:
    def __init__(self, color, kind):
        self.color = color 
        self.kind = kind   

    def validate_move_by_piece_rules(self, board, start, end):
        raise NotImplementedError

    def __str__(self):
        return self.color + self.kind


class King(Piece):
    def __init__(self, color):
        super().__init__(color, 'K')

    def validate_move_by_piece_rules(self, board, start, end):
        sr, sc = start
        er, ec = end
        return abs(er - sr) <= 1 and abs(ec - sc) <= 1


class Knight(Piece):
    def __init__(self, color):
        super().__init__(color, 'N')

    def validate_move_by_piece_rules(self, board, start, end):
        sr, sc = start
        er, ec = end
        return (abs(er - sr) == 1 and abs(ec - sc) == 2) or \
               (abs(er - sr) == 2 and abs(ec - sc) == 1)


class Rook(Piece):
    def __init__(self, color):
        super().__init__(color, 'R')

    def _has_blocker(self, board, sr, sc, er, ec):
        if sc == ec:  
            step = 1 if sr < er else -1
            for r in range(sr + step, er, step):
                if board[r][sc] != EMPTY_CELL:
                    return True
        elif sr == er:  
            step = 1 if sc < ec else -1
            for c in range(sc + step, ec, step):
                if board[sr][c] != EMPTY_CELL:
                    return True
        return False

    def validate_move_by_piece_rules(self, board, start, end):
        sr, sc = start
        er, ec = end
        if sr != er and sc != ec:  
            return False  
        return not self._has_blocker(board, sr, sc, er, ec)


class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color, 'B')

    def _has_blocker(self, board, sr, sc, er, ec):
        step_row = 1 if sr < er else -1
        step_col = 1 if sc < ec else -1
        r, c = sr + step_row, sc + step_col
        while r != er and c != ec:
            if board[r][c] != EMPTY_CELL:
                return True
            r += step_row
            c += step_col
        return False

    def validate_move_by_piece_rules(self, board, start, end):
        sr, sc = start
        er, ec = end
        if abs(er - sr) != abs(ec - sc):
            return False 
        return not self._has_blocker(board, sr, sc, er, ec)


class Queen(Piece):

    def __init__(self, color):
        super().__init__(color, 'Q')
        self._rook = Rook(color)
        self._bishop = Bishop(color)

    def validate_move_by_piece_rules(self, board, start, end):
        return self._rook.validate_move_by_piece_rules(board, start, end) or \
               self._bishop.validate_move_by_piece_rules(board, start, end)


class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color, 'P')

    def validate_move_by_piece_rules(self, board, start, end):
        sr, sc = start
        er, ec = end
        row_step = -1 if self.color == 'w' else 1  
        col_diff = abs(ec - sc)
        actual_row_diff = er - sr

        if actual_row_diff == row_step and col_diff == 0:
            return board[er][ec] == EMPTY_CELL

        elif actual_row_diff == 2 * row_step and col_diff == 0:
            is_start = (self.color == 'w' and sr == len(board) - 2) or \
               (self.color == 'b' and sr == 1)
            middle_row = sr + row_step
            return is_start and board[middle_row][sc] == EMPTY_CELL and board[er][ec] == EMPTY_CELL

        elif actual_row_diff == row_step and col_diff == 1:
            return board[er][ec] != EMPTY_CELL

        return False


def create_piece(piece_str):
    color = piece_str[0]
    kind = piece_str[1]
    return PIECE_CLASSES[kind](color)
    

PIECE_CLASSES = {
    'K': King,
    'Q': Queen,
    'R': Rook,
    'B': Bishop,
    'N': Knight,
    'P': Pawn,
}
from core.domain.board import Board
from core.config.constants import WHITE_COLOR, BLACK_COLOR

BACK_ROW = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
PAWN = 'P'


def create_standard_board(size=8):
    grid = [['.'] * size for _ in range(size)]
    for i, kind in enumerate(BACK_ROW):
        grid[size - 1][i] = WHITE_COLOR + kind
        grid[0][i] = BLACK_COLOR + kind
    for i in range(size):
        grid[size - 2][i] = WHITE_COLOR + PAWN
        grid[1][i] = BLACK_COLOR + PAWN
    return Board(grid)

EMPTY_CELL = '.'
WHITE_COLOR = 'w'
BLACK_COLOR = 'b'
MS_PER_CELL = 1000


class Board:
    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])

    def is_empty(self, row, col) -> bool:
        return self.grid[row][col] == EMPTY_CELL

    def get_piece_color(self, row, col):
        if self.is_empty(row, col):
            return None
        return self.grid[row][col][0]

    def get_piece_kind(self, row, col):
        if self.is_empty(row, col):
            return None
        return self.grid[row][col][1]

    def get_piece_str(self, row, col):
        if self.is_empty(row, col):
            return None
        return self.grid[row][col]

    def set_piece(self, row, col, piece_str):
        self.grid[row][col] = piece_str

    def clear_cell(self, row, col):
        self.grid[row][col] = EMPTY_CELL

    def is_in_bounds(self, row, col) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def __str__(self):
        return '\n'.join(' '.join(row) for row in self.grid)

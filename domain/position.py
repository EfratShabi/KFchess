class Position:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.row == other.row and self.col == other.col
        return NotImplemented

    def __iter__(self):
        yield self.row
        yield self.col

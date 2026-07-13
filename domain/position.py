class Position:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def as_tuple(self):
        return (self.row, self.col)

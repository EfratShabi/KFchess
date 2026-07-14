CELL_SIZE = 100

def pixel_to_cell(x, y):
    col = x // CELL_SIZE
    row = y // CELL_SIZE
    return row, col
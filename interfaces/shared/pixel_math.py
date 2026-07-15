from interfaces.shared.graphics_constants import CELL_SIZE

def pixel_to_cell(x, y):
    col = x // CELL_SIZE
    row = y // CELL_SIZE
    return row, col

def cell_to_pixel(row, col, cell_size=100, offset_x=0, offset_y=0):
    x = offset_x + (col * cell_size)
    y = offset_y + (row * cell_size)
    return x, y

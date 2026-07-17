from interfaces.shared.graphics_constants import CELL_SIZE

def pixel_to_cell(x, y):
    col = x // CELL_SIZE
    row = y // CELL_SIZE
    return row, col

def cell_to_pixel(row, col, cell_size, offset_x=0, offset_y=0):
    x = offset_x + (col * cell_size)
    y = offset_y + (row * cell_size)
    return x, y

def interpolate_pixel(start, end, progress, cell_size, offset_x=0, offset_y=0):
    start_row, start_col = start
    end_row, end_col = end
    x1, y1 = cell_to_pixel(start_row, start_col, cell_size, offset_x, offset_y)
    x2, y2 = cell_to_pixel(end_row, end_col, cell_size, offset_x, offset_y)
    x = x1 + (x2 - x1) * progress
    y = y1 + (y2 - y1) * progress
    return x, y

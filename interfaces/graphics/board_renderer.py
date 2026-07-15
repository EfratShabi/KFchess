import os
from interfaces.graphics.image_commands import Img
from interfaces.shared.pixel_math import cell_to_pixel
from interfaces.shared.graphics_constants import CELL_SIZE, BOARD_SIZE, BOARD_IMAGE_PATH


class BoardRenderer:
    def __init__(self, assets_path="assets"):
        self.assets_path = assets_path
        self.canvas = None

    def draw_empty_board(self):
        pixel_size = CELL_SIZE * BOARD_SIZE
        self.canvas = Img().read(BOARD_IMAGE_PATH, size=(pixel_size, pixel_size))
        return self

    def draw_board(self, grid):
        self.draw_empty_board()
        for row_idx, row in enumerate(grid):
            for col_idx, piece_str in enumerate(row):
                if piece_str and piece_str != '.':
                    self.draw_piece(piece_str, row_idx, col_idx)
        return self

    def draw_piece(self, piece_str, row, col):
        color, kind = piece_str[0], piece_str[1]
        folder = kind + ('W' if color == 'w' else 'B')
        piece_path = os.path.join(
            self.assets_path, "pieces1", folder, "states", "idle", "sprites", "1.png"
        )
        piece_img = Img().read(piece_path, size=(CELL_SIZE, CELL_SIZE), keep_aspect=True)
        x, y = cell_to_pixel(row, col, cell_size=CELL_SIZE)
        piece_img.draw_on(self.canvas, x, y)
        return self

    def show(self):
        self.canvas.show()


if __name__ == "__main__":
    BoardRenderer().draw_empty_board().show()

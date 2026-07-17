import os
from interfaces.graphics.image_commands import Img
from interfaces.graphics.sprite_loader import compute_frame_index
from interfaces.shared.pixel_math import cell_to_pixel, interpolate_pixel
from interfaces.shared.graphics_constants import CELL_SIZE, BOARD_SIZE, BOARD_IMAGE_PATH
from core.config.constants import WHITE_COLOR, BLACK_COLOR,EMPTY_CELL

FOLDER_COLOR = {WHITE_COLOR: 'W', BLACK_COLOR: 'B'}


class BoardRenderer:
    def __init__(self, assets_path="assets"):
        self.assets_path = assets_path
        self.canvas = None

    def draw_empty_board(self):
        pixel_size = CELL_SIZE * BOARD_SIZE
        self.canvas = Img().read(BOARD_IMAGE_PATH, size=(pixel_size, pixel_size))
        return self

    def draw_board(self, service):
        self.draw_empty_board()
        grid = service.get_board_grid()
        for row_idx, row in enumerate(grid):
            for col_idx, piece_str in enumerate(row):
                if piece_str and piece_str != EMPTY_CELL:
                    piece_state = service.get_piece_state(row_idx, col_idx)
                    state_name, elapsed_ms = piece_state if piece_state else ("idle", 0)

                    movement = service.get_piece_movement(row_idx, col_idx)
                    if movement is not None:
                        start, end, progress = movement
                        x, y = interpolate_pixel(start, end, progress, cell_size=CELL_SIZE)
                    else:
                        x, y = cell_to_pixel(row_idx, col_idx, cell_size=CELL_SIZE)

                    self.draw_piece(piece_str, x, y, state=state_name, elapsed_ms=elapsed_ms)
        return self

    def get_sprite_path(self, piece_name, state, frame):
        return os.path.join(
            self.assets_path, "pieces1", piece_name, "states", state, "sprites", f"{frame}.png")


    def draw_piece(self, piece_str, x, y, state, elapsed_ms):
        color, kind = piece_str[0], piece_str[1]
        folder = kind + FOLDER_COLOR[color]

        frame = compute_frame_index(self.assets_path, folder, state, elapsed_ms)
        piece_path = self.get_sprite_path(folder, state=state, frame=frame)

        piece_img = Img().read(piece_path, size=(CELL_SIZE, CELL_SIZE), keep_aspect=True)
        # חישוב אופסט למרכוז הכלי בתוך התא:
        # אנחנו לוקחים את ההפרש בין גודל התא לגודל הכלי ומחלקים ב-2
        # כדי ליצור שוליים שווים משני הצדדים.
        h, w = piece_img.img.shape[:2]
        x = int(x) + (CELL_SIZE - w) // 2
        y = int(y) + (CELL_SIZE - h) // 2
        piece_img.draw_on(self.canvas, x, y)
        return self

    def show(self):
        self.canvas.show()



if __name__ == "__main__":
    BoardRenderer().draw_empty_board().show()

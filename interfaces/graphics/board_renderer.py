import os
from interfaces.graphics.image_commands import Img
from interfaces.graphics.sprite_loader import compute_frame_index
from interfaces.shared.pixel_math import cell_to_pixel, interpolate_pixel
from interfaces.shared.graphics_constants import (
    CELL_SIZE, BOARD_SIZE, BOARD_IMAGE_PATH, PIECES_FOLDER,
    TEXT_COLOR_WHITE, TEXT_COLOR_RED,
    CANVAS_WIDTH, CANVAS_HEIGHT, BOARD_OFFSET_X, BOARD_OFFSET_Y,
    LOG_PANEL_X, LOG_LINE_HEIGHT, LOG_FONT_SIZE,
)
from core.config.constants import WHITE_COLOR, BLACK_COLOR,EMPTY_CELL
from core.domain.time_span import TimeSpan

FOLDER_COLOR = {WHITE_COLOR: 'W', BLACK_COLOR: 'B'}


class BoardRenderer:
    def __init__(self, assets_path="assets"):
        self.assets_path = assets_path
        self.canvas = None

    def draw_empty_board(self):
        board_pixel_size = CELL_SIZE * BOARD_SIZE
        self.canvas = Img.blank(CANVAS_WIDTH, CANVAS_HEIGHT)
        board_img = Img().read(BOARD_IMAGE_PATH, size=(board_pixel_size, board_pixel_size))
        board_img.draw_on(self.canvas, BOARD_OFFSET_X, BOARD_OFFSET_Y)
        return self

    def draw_board(self, service):
        self.draw_empty_board()
        grid = service.get_board_grid()
        for row_idx, row in enumerate(grid):
            for col_idx, piece_str in enumerate(row):
                if piece_str and piece_str != EMPTY_CELL:
                    piece_state = service.get_piece_state(row_idx, col_idx)
                    state_name, time_span = piece_state if piece_state else ("idle", TimeSpan(0, 0))
                    movement = service.get_piece_movement(row_idx, col_idx)
                    if movement is not None:
                        start, end, progress = movement
                        x, y = interpolate_pixel(start, end, progress, cell_size=CELL_SIZE,
                                                  offset_x=BOARD_OFFSET_X, offset_y=BOARD_OFFSET_Y)
                    else:
                        x, y = cell_to_pixel(row_idx, col_idx, cell_size=CELL_SIZE,
                                              offset_x=BOARD_OFFSET_X, offset_y=BOARD_OFFSET_Y)

                    self.draw_piece(piece_str, x, y, state=state_name, time_span=time_span)
        return self



    def get_sprite_path(self, piece_name, state, frame):
        return os.path.join(
            self.assets_path, PIECES_FOLDER, piece_name, "states", state, "sprites", f"{frame}.png")


    def draw_piece(self, piece_str, x, y, state, time_span):
        color, kind = piece_str[0], piece_str[1]
        folder = kind + FOLDER_COLOR[color]

        frame = compute_frame_index(self.assets_path, folder, state, time_span.elapsed_ms())
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

    def draw_scores(self, service):
        scores = service.get_scores()
        self.canvas.put_text(f"White: {scores[WHITE_COLOR]}", 10, 30,
                              font_size=1, color=TEXT_COLOR_WHITE, thickness=2)
        self.canvas.put_text(f"Black: {scores[BLACK_COLOR]}", CELL_SIZE * BOARD_SIZE - 160, 30,
                              font_size=1, color=TEXT_COLOR_WHITE, thickness=2)
        return self

    def draw_event_log(self, service):
        log = service.get_event_log()
        header_y = BOARD_OFFSET_Y + LOG_LINE_HEIGHT
        self.canvas.put_text("Moves Log", LOG_PANEL_X, header_y,
                              font_size=LOG_FONT_SIZE, color=TEXT_COLOR_WHITE, thickness=1)

        max_lines = (CANVAS_HEIGHT - BOARD_OFFSET_Y) // LOG_LINE_HEIGHT - 1
        visible = log[-max_lines:]
        for i, line in enumerate(visible):
            y = header_y + (i + 1) * LOG_LINE_HEIGHT
            self.canvas.put_text(line, LOG_PANEL_X, y,
                                  font_size=LOG_FONT_SIZE, color=TEXT_COLOR_WHITE, thickness=1)
        return self

    def draw_game_over_message(self):
        """מציירת הודעת 'Game Over' באדום, ממורכזת בקירוב על הלוח (150 הוא הזחה ידנית לפי רוחב הטקסט המשוער)."""
        pixel_size = CELL_SIZE * BOARD_SIZE
        self.canvas.put_text("Game Over", pixel_size // 2 - 150, BOARD_OFFSET_Y + pixel_size // 2,
                              font_size=2, color=TEXT_COLOR_RED, thickness=3)
        return self


    def show(self):
        self.canvas.show()



if __name__ == "__main__":
    BoardRenderer().draw_empty_board().show()

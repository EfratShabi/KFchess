from interfaces.shared.pixel_math import pixel_to_cell
import cv2

class InputController:
    def __init__(self, game_service):
        self.game_service = game_service
        self.selected_piece = None

    def handle_click(self, x, y):
        pos = pixel_to_cell(x, y)
        if not self.game_service.board.is_in_bounds(*pos):
            return
        if self._is_busy(pos):
            self.selected_piece = None
            return
        if self.selected_piece is None:
            self._select(pos)
            return
        if self._is_own_piece(pos):
            self._select(pos)
            return
        self.game_service.try_move(self.selected_piece, pos)
        self.selected_piece = None

    def handle_jump(self, x, y):
        row, col = pixel_to_cell(x, y)
        self.game_service.try_jump(row, col)
        self.selected_piece = None

    def _select(self, pos):
        if not self.game_service.board.is_empty(*pos):
            self.selected_piece = pos

    def _is_busy(self, pos):
        row, col = pos
        return self.game_service.state.is_moving(row, col)

    def _is_own_piece(self, pos):
        if self.game_service.board.is_empty(*pos):
            return False
        return self.game_service.board.get_piece_color(*pos) == self.game_service.board.get_piece_color(*self.selected_piece)
    

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.handle_click(x, y)
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.handle_jump(x, y)

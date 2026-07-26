import cv2

import protocol
from interfaces.shared.graphics_constants import BOARD_OFFSET_X, BOARD_OFFSET_Y
from interfaces.shared.pixel_math import pixel_to_cell
from protocol import FIELDS, MSG_TYPES


class NetworkedInputController:
    """Translates mouse clicks into MOVE/JUMP protocol messages sent to the server.
    Never touches game rules — selection here is UX only, the server is the sole authority."""

    def __init__(self, client_state, network_client, my_color):
        self.state = client_state
        self.network_client = network_client
        self.my_color = my_color
        self.selected_piece = None

    def handle_click(self, x, y):
        pos = pixel_to_cell(x - BOARD_OFFSET_X, y - BOARD_OFFSET_Y)
        if not self.state.board.is_in_bounds(*pos):
            return
        if self._is_busy(pos):
            self.selected_piece = None
            return
        self._handle_selection(pos)

    def _handle_selection(self, pos):
        if self.selected_piece is None:
            self._select(pos)
            return
        if self._is_own_piece(pos):
            self._select(pos)
            return
        self._send_move(self.selected_piece, pos)
        self.selected_piece = None

    def handle_jump(self, x, y):
        pos = pixel_to_cell(x - BOARD_OFFSET_X, y - BOARD_OFFSET_Y)
        if not self._is_valid_jump_target(pos):
            return
        row, col = pos
        self._send_jump(row, col)
        self.selected_piece = None

    def _is_valid_jump_target(self, pos):
        if not self.state.board.is_in_bounds(*pos):
            return False
        if self.state.board.is_empty(*pos):
            return False
        return self.state.board.get_piece_color(*pos) == self.my_color

    def _select(self, pos):
        if not self.state.board.is_empty(*pos) and self._is_own_piece(pos):
            self.selected_piece = pos

    def _is_busy(self, pos):
        row, col = pos
        if self.state.board.is_empty(row, col):
            return False
        state_name, _ = self.state.get_piece_state(row, col)
        return state_name != 'idle'

    def _is_own_piece(self, pos):
        if self.state.board.is_empty(*pos):
            return False
        return self.state.board.get_piece_color(*pos) == self.my_color

    def _send_move(self, start, end):
        raw = protocol.encode(MSG_TYPES['MOVE'], **{
            FIELDS['START']: list(start),
            FIELDS['END']: list(end),
        })
        self.network_client.send(raw)

    def _send_jump(self, row, col):
        raw = protocol.encode(MSG_TYPES['JUMP'], **{
            FIELDS['ROW']: row,
            FIELDS['COL']: col,
        })
        self.network_client.send(raw)

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.handle_click(x, y)
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.handle_jump(x, y)

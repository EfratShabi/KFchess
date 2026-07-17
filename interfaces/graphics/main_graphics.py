import time
import cv2
from core.domain.board_factory import create_standard_board
from core.real_time.real_time import RealTime
from core.services.game_service import GameService
from interfaces.graphics.board_renderer import BoardRenderer
from interfaces.shared.input_controller import InputController



def main():
    board = create_standard_board()
    state = RealTime()
    service = GameService(board, state)
    renderer = BoardRenderer()

    controller = InputController(service, board)
    window_name = "KF Chess"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, controller.mouse_callback)

    last_tick = time.perf_counter()
    while True:
        now = time.perf_counter()
        delta_ms = int((now - last_tick) * 1000)
        last_tick = now

        service.process_wait(delta_ms)
        renderer.draw_board(service)
        cv2.imshow(window_name, renderer.canvas.img)
        if cv2.waitKey(1) & 0xFF == 27:
            break

if __name__ == "__main__":
    main()
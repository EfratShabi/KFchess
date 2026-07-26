import time
import cv2
from interfaces.shared.graphics_constants import ESC_KEY


class GameLoopRunner:
    """Owns the cv2 window lifecycle and the render/poll loop.
    Knows nothing about game rules or networking — per-tick logic is injected via on_tick."""

    def __init__(self, window_name, renderer, controller, state, on_tick):
        self.window_name = window_name
        self.renderer = renderer
        self.controller = controller
        self.state = state
        self.on_tick = on_tick

    def run(self):
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.controller.mouse_callback)

        last_tick = time.perf_counter()
        try:
            while True:
                now = time.perf_counter()
                delta_ms = int((now - last_tick) * 1000)
                last_tick = now

                self.on_tick(delta_ms)

                self.renderer.draw_board(self.state)
                self.renderer.draw_scores(self.state)
                self.renderer.draw_event_log(self.state)
                if self.state.is_game_over():
                    self.renderer.draw_game_over_message()
                cv2.imshow(self.window_name, self.renderer.canvas.img)
                if cv2.waitKey(1) & 0xFF == ESC_KEY:
                    break
        finally:
            cv2.destroyWindow(self.window_name)

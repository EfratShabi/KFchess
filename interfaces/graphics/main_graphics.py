from core.domain.board_factory import create_standard_board
from core.real_time.real_time import RealTime
from core.services.game_service import GameService
from interfaces.graphics.board_renderer import BoardRenderer
from interfaces.shared.input_controller import InputController
from interfaces.shared.game_loop_runner import GameLoopRunner


def main():
    board = create_standard_board()
    state = RealTime()
    service = GameService(board, state)
    renderer = BoardRenderer()
    controller = InputController(service)

    GameLoopRunner(
        window_name="KF Chess",
        renderer=renderer,
        controller=controller,
        state=service,
        on_tick=service.process_wait,
    ).run()

if __name__ == "__main__":
    main()
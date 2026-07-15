from core.domain.board_factory import create_standard_board
from core.real_time.real_time import RealTime
from core.services.game_service import GameService
from interfaces.shared.input_controller import InputController
from interfaces.graphics.board_renderer import BoardRenderer


def main():
    board = create_standard_board()
    state = RealTime()
    service = GameService(board, state)
    renderer = BoardRenderer()

    renderer.draw_board(service.get_board_grid())
    renderer.show()


if __name__ == "__main__":
    main()

from core.domain.board import Board
from core.real_time.real_time import RealTime
from core.services.game_service import GameService
from interfaces.shared.input_controller import InputController
from interfaces.graphics.board_renderer import BoardRenderer


def main():
    grid = [["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            [".", ".", ".", ".", ".", ".", ".", "."],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"]]

    board = Board(grid)
    state = RealTime()
    service = GameService(board, state)
    renderer = BoardRenderer()

    renderer.draw_board(service.get_board_grid())
    renderer.show()


if __name__ == "__main__":
    main()

from core.domain.board import Board
from core.real_time.real_time import RealTime
from core.services.game_service import GameService


def make_service(*rows):
    grid = [r.split() for r in rows]
    board = Board(grid)
    return GameService(board, RealTime())


def test_move_landing_does_not_raise_and_is_logged():
    service = make_service("wR . .")

    service.try_move((0, 0), (0, 2))
    service.process_wait(2000)

    assert service.board.get_piece_str(0, 2) == 'wR'
    assert any('arrived' in entry for entry in service.get_event_log())

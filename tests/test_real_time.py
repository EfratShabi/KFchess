import asyncio

from core.config.constants import WHITE_COLOR
from core.domain.board import Board
from core.real_time.real_time import RealTime
from core.services.game_service import GameService
from server.session.broadcaster import NetworkBroadcaster


def make_service(*rows):
    grid = [r.split() for r in rows]
    board = Board(grid)
    return GameService(board, RealTime())


def test_force_game_over_sets_winner_and_game_over_flag():
    service = make_service("wK . .")

    service.force_game_over(WHITE_COLOR)

    assert service.is_game_over() is True
    assert service.get_winner() == WHITE_COLOR


def test_force_game_over_notifies_observers():
    service = make_service("wK . .")
    broadcaster = NetworkBroadcaster()
    service.state.add_observer(broadcaster)

    service.force_game_over(WHITE_COLOR)

    message = asyncio.run(broadcaster.queue.get())
    assert message.event == 'game_over'
    assert message.winner == WHITE_COLOR

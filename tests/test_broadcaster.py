from core.domain.board import Board
from core.real_time.real_time import RealTime
from core.services.game_service import GameService
from server.broadcaster import NetworkBroadcaster


def make_service(*rows):
    grid = [r.split() for r in rows]
    board = Board(grid)
    return GameService(board, RealTime())


def test_move_started_event_appears_in_outbox():
    service = make_service("wR . .")
    broadcaster = NetworkBroadcaster()
    service.state.add_observer(broadcaster)

    service.try_move((0, 0), (0, 2))

    message = broadcaster.drain()[0]
    assert message['type'] == 'state_update'
    assert message['event'] == 'move_started'
    assert message['piece'] == 'wR'


def test_jump_started_serializes_position_cell_to_list():
    service = make_service("wK . .")
    broadcaster = NetworkBroadcaster()
    service.state.add_observer(broadcaster)

    service.try_jump(0, 0)

    message = broadcaster.drain()[0]
    assert message['event'] == 'jump_started'
    assert message['cell'] == [0, 0]
    assert message['piece'] == 'wK'


def test_drain_empties_the_outbox():
    service = make_service("wK . .")
    broadcaster = NetworkBroadcaster()
    service.state.add_observer(broadcaster)

    service.try_jump(0, 0)
    broadcaster.drain()

    assert broadcaster.drain() == []


def test_broadcaster_coexists_with_existing_game_logger():
    service = make_service("wK . .")
    broadcaster = NetworkBroadcaster()
    service.state.add_observer(broadcaster)

    service.try_jump(0, 0)

    assert len(service.get_event_log()) == 1
    assert len(broadcaster.drain()) == 1

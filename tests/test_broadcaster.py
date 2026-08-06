import asyncio

from core.domain.board import Board
from core.real_time.real_time import RealTime
from core.services.game_service import GameService
from server.session.broadcaster import NetworkBroadcaster
from protocol import JumpStarted, MoveStarted


def make_service(*rows):
    grid = [r.split() for r in rows]
    board = Board(grid)
    return GameService(board, RealTime())


def test_move_started_event_appears_in_queue():
    service = make_service("wR . .")
    broadcaster = NetworkBroadcaster()
    service.state.add_observer(broadcaster)

    service.try_move((0, 0), (0, 2))

    message = asyncio.run(broadcaster.queue.get())
    assert isinstance(message, MoveStarted)
    assert message.type == 'state_update'
    assert message.event == 'move_started'
    assert message.piece == 'wR'
    # start/end arrive from core as plain tuples (not Position), so serialize() leaves them untouched
    assert tuple(message.start) == (0, 0)
    assert tuple(message.end) == (0, 2)


def test_jump_started_serializes_position_cell_to_list():
    service = make_service("wK . .")
    broadcaster = NetworkBroadcaster()
    service.state.add_observer(broadcaster)

    service.try_jump(0, 0)

    message = asyncio.run(broadcaster.queue.get())
    assert isinstance(message, JumpStarted)
    assert message.event == 'jump_started'
    assert message.cell == [0, 0]
    assert message.piece == 'wK'


def test_queue_is_empty_after_being_consumed():
    service = make_service("wK . .")
    broadcaster = NetworkBroadcaster()
    service.state.add_observer(broadcaster)

    service.try_jump(0, 0)
    asyncio.run(broadcaster.queue.get())

    assert broadcaster.queue.empty()


def test_broadcaster_coexists_with_existing_game_logger():
    service = make_service("wK . .")
    broadcaster = NetworkBroadcaster()
    service.state.add_observer(broadcaster)

    service.try_jump(0, 0)

    assert len(service.get_event_log()) == 1
    assert broadcaster.queue.qsize() == 1

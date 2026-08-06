import asyncio

from core.domain.position import Position
from protocol import (
    GameOver, JumpLanded, JumpStarted, MidairCapture, MoveCaptured, MoveLanded, MoveStarted, position_to_list,
)


def _serialize_value(value):
    if isinstance(value, Position):
        return position_to_list(value)
    return value


def serialize(data):
    return {key: _serialize_value(value) for key, value in data.items()}


EVENT_CLASSES = {
    'move_started': MoveStarted,
    'jump_started': JumpStarted,
    'move_landed': MoveLanded,
    'jump_landed': JumpLanded,
    'move_captured': MoveCaptured,
    'midair_capture': MidairCapture,
    'game_over': GameOver,
}


class NetworkBroadcaster:
    def __init__(self):
        self.queue = asyncio.Queue()

    def on_event(self, event_type, **data):
        message = EVENT_CLASSES[event_type](**serialize(data))
        self.queue.put_nowait(message)

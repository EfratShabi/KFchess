from core.domain.position import Position
from server.protocol import MSG_TYPES, position_to_list


def _serialize_value(value):
    if isinstance(value, Position):
        return position_to_list(value)
    return value


def serialize(data):
    return {key: _serialize_value(value) for key, value in data.items()}


class NetworkBroadcaster:
    def __init__(self):
        self.outbox = []

    def on_event(self, event_type, **data):
        self.outbox.append({'type': MSG_TYPES['STATE_UPDATE'], 'event': event_type, **serialize(data)})

    def drain(self):
        messages, self.outbox = self.outbox, []
        return messages

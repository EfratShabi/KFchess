import json


MSG_TYPES = {
    'REGISTER': 'register',
    'LOGIN': 'login',
    'OK': 'ok',
    'ERROR': 'error',
    'JOIN_QUEUE': 'join_queue',
    'MATCH_FOUND': 'match_found',
    'NO_OPPONENT': 'no_opponent',
    'MOVE': 'move',
    'JUMP': 'jump',
    'STATE_UPDATE': 'state_update',
    'GAME_OVER': 'game_over',
}


class ProtocolError(Exception):
    pass


def encode(msg_type, **payload):
    return json.dumps({'type': msg_type, **payload})


def decode(raw):
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ProtocolError(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict) or 'type' not in data:
        raise ProtocolError("message missing 'type' field")
    return data


def position_to_list(pos):
    return [pos.row, pos.col]

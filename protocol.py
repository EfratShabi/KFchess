import json
from dataclasses import asdict, dataclass, fields

from core.domain.position import Position


MSG_TYPES = {
    'REGISTER': 'register',
    'LOGIN': 'login',
    'AUTHENTICATE': 'authenticate',
    'OK': 'ok',
    'ERROR': 'error',
    'JOIN_QUEUE': 'join_queue',
    'RECONNECT': 'reconnect',
    'MATCH_FOUND': 'match_found',
    'NO_OPPONENT': 'no_opponent',
    'OPPONENT_DISCONNECTED': 'opponent_disconnected',
    'MOVE': 'move',
    'JUMP': 'jump',
    'STATE_UPDATE': 'state_update',
    'GAME_OVER': 'game_over',
}

FIELDS = {
    'TYPE': 'type',
    'USERNAME': 'username',
    'PASSWORD': 'password',
    'TOKEN': 'token',
    'TICKET': 'ticket',
    'ROOM_ID': 'room_id',
    'COLOR': 'color',
    'OPPONENT': 'opponent',
    'START': 'start',
    'END': 'end',
    'ROW': 'row',
    'COL': 'col',
    'EVENT': 'event',
    'PIECES': 'pieces',
    'SCORES': 'scores',
    'GAME_OVER': 'game_over',
    'MESSAGE': 'message',
    'PIECE': 'piece',
    'STATE': 'state',
    'PROGRESS': 'progress',
    'NEXT_STATE': 'next_state',
}


class ProtocolError(Exception):
    pass


@dataclass
class Ok:
    type: str = MSG_TYPES['OK']


@dataclass
class ErrorMessage:
    message: str
    type: str = MSG_TYPES['ERROR']


@dataclass
class MatchFound:
    room_id: str
    color: str
    opponent: str
    ticket: str
    type: str = MSG_TYPES['MATCH_FOUND']


@dataclass
class NoOpponent:
    type: str = MSG_TYPES['NO_OPPONENT']


@dataclass
class OpponentDisconnected:
    type: str = MSG_TYPES['OPPONENT_DISCONNECTED']


@dataclass
class OpponentReconnecting:
    type: str = MSG_TYPES['STATE_UPDATE']
    event: str = 'opponent_reconnecting'


@dataclass
class PieceSnapshot:
    piece: str
    state: str
    start: list = None
    end: list = None
    progress: float = None


@dataclass
class Snapshot:
    pieces: dict
    scores: dict
    game_over: bool
    event: str = 'snapshot'
    type: str = MSG_TYPES['STATE_UPDATE']


@dataclass
class MoveStarted:
    piece: str
    start: list
    end: list
    time: int
    event: str = 'move_started'
    type: str = MSG_TYPES['STATE_UPDATE']


@dataclass
class JumpStarted:
    piece: str
    cell: list
    time: int
    event: str = 'jump_started'
    type: str = MSG_TYPES['STATE_UPDATE']


@dataclass
class MoveLanded:
    piece: str
    end: list
    next_state: str
    time: int
    event: str = 'move_landed'
    type: str = MSG_TYPES['STATE_UPDATE']


@dataclass
class JumpLanded:
    piece: str
    cell: list
    next_state: str
    time: int
    event: str = 'jump_landed'
    type: str = MSG_TYPES['STATE_UPDATE']


@dataclass
class MoveCaptured:
    attacker: str
    captured: str
    position: list
    time: int
    event: str = 'move_captured'
    type: str = MSG_TYPES['STATE_UPDATE']


@dataclass
class MidairCapture:
    attacker: str
    captured: str
    position: list
    time: int
    event: str = 'midair_capture'
    type: str = MSG_TYPES['STATE_UPDATE']


@dataclass
class GameOver:
    winner: str
    time: int
    event: str = 'game_over'
    type: str = MSG_TYPES['STATE_UPDATE']


def encode(msg_type, **payload):
    return json.dumps({FIELDS['TYPE']: msg_type, **payload})


def encode_message(message):
    return json.dumps(asdict(message))


def decode(raw):
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ProtocolError(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict) or FIELDS['TYPE'] not in data:
        raise ProtocolError("message missing 'type' field")
    return data


MESSAGE_CLASSES = {
    MSG_TYPES['OK']: Ok,
    MSG_TYPES['ERROR']: ErrorMessage,
    MSG_TYPES['MATCH_FOUND']: MatchFound,
    MSG_TYPES['NO_OPPONENT']: NoOpponent,
    MSG_TYPES['OPPONENT_DISCONNECTED']: OpponentDisconnected,
    'opponent_reconnecting': OpponentReconnecting,
    'snapshot': Snapshot,
    'move_started': MoveStarted,
    'jump_started': JumpStarted,
    'move_landed': MoveLanded,
    'jump_landed': JumpLanded,
    'move_captured': MoveCaptured,
    'midair_capture': MidairCapture,
    'game_over': GameOver,
}


def decode_message(raw):
    data = decode(raw)
    key = data.get(FIELDS['EVENT'], data[FIELDS['TYPE']])
    message_class = MESSAGE_CLASSES.get(key)
    if message_class is None:
        raise ProtocolError(f"unknown message: {key}")
    if message_class is Snapshot:
        data = {**data, FIELDS['PIECES']: {k: PieceSnapshot(**v) for k, v in data[FIELDS['PIECES']].items()}}
    field_names = {f.name for f in fields(message_class)}
    return message_class(**{k: v for k, v in data.items() if k in field_names})


def position_to_list(pos):
    return [pos.row, pos.col]


def list_to_position(lst):
    row, col = lst
    return Position(row, col)

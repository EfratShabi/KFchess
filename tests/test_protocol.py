import json

import pytest

from core.domain.position import Position
from server.protocol import encode, decode, position_to_list, ProtocolError, MSG_TYPES


def test_encode_includes_type_and_payload():
    raw = encode(MSG_TYPES['MOVE'], row=1, col=2)
    data = json.loads(raw)
    assert data == {'type': 'move', 'row': 1, 'col': 2}


def test_decode_round_trips_encode():
    raw = encode(MSG_TYPES['LOGIN'], username='efrat')
    assert decode(raw) == {'type': 'login', 'username': 'efrat'}


def test_decode_rejects_invalid_json():
    with pytest.raises(ProtocolError):
        decode("not json")


def test_decode_rejects_missing_type():
    with pytest.raises(ProtocolError):
        decode(json.dumps({'row': 1, 'col': 2}))


def test_decode_rejects_non_object_json():
    with pytest.raises(ProtocolError):
        decode(json.dumps([1, 2, 3]))


def test_position_to_list():
    assert position_to_list(Position(3, 5)) == [3, 5]

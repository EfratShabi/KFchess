import protocol
from protocol import FIELDS, MSG_TYPES, ErrorMessage, Ok, ProtocolError
from server.session import SessionStatus
from server.tokens import verify_ticket


async def try_reconnect(websocket, player, sessions):
    async for raw in websocket:
        try:
            msg = protocol.decode(raw)
        except ProtocolError:
            continue
        if msg[FIELDS['TYPE']] != MSG_TYPES['RECONNECT']:
            continue

        result = verify_ticket(msg.get(FIELDS['TICKET']))
        if result is None:
            await websocket.send(protocol.encode_message(ErrorMessage(message='invalid or expired ticket')))
            continue
        room_id, _epoch = result

        session = sessions.get(room_id)
        if session is None or session.status != SessionStatus.ACTIVE:
            await websocket.send(protocol.encode_message(ErrorMessage(message='room no longer active')))
            return None

        color = session.color_of_username(player.username)
        if color is None:
            await websocket.send(protocol.encode_message(ErrorMessage(message='not a player in this room')))
            return None

        session.mark_reconnected(color, player)
        await player.send(Ok())
        return session
    return None

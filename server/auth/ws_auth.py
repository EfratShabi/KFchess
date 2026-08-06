import protocol
from server.session.connection import PlayerConnection
from server.auth.tokens import verify_token
from protocol import FIELDS, MSG_TYPES, ErrorMessage, Ok, ProtocolError


async def authenticate_with_token(websocket, repo):
    async for raw in websocket:
        try:
            msg = protocol.decode(raw)
        except ProtocolError:
            continue
        if msg[FIELDS['TYPE']] != MSG_TYPES['AUTHENTICATE']:
            continue

        username = verify_token(msg.get(FIELDS['TOKEN']))
        rating = repo.get_rating(username) if username else None
        if rating is None:
            await websocket.send(protocol.encode_message(ErrorMessage(message='invalid or expired token')))
            continue

        conn = PlayerConnection(websocket, username, rating)
        await conn.send(Ok())
        return conn
    return None

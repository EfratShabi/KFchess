import protocol
from server.connection import PlayerConnection
from protocol import FIELDS, MSG_TYPES, ErrorMessage, Ok, ProtocolError


async def authenticate(websocket, repo):
    async for raw in websocket:
        try:
            msg = protocol.decode(raw)
        except ProtocolError:
            continue

        username = msg.get(FIELDS['USERNAME'])
        password = msg.get(FIELDS['PASSWORD'])
        if msg[FIELDS['TYPE']] == MSG_TYPES['REGISTER'] and username and password:
            ok = repo.register(username, password)
        elif msg[FIELDS['TYPE']] == MSG_TYPES['LOGIN'] and username and password:
            ok = repo.authenticate(username, password)
        else:
            ok = False

        if ok:
            conn = PlayerConnection(websocket, username, repo.get_rating(username))
            await conn.send(Ok())
            return conn
        await websocket.send(protocol.encode_message(ErrorMessage(message='login failed')))
    return None

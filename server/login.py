from server import protocol
from server.connection import PlayerConnection
from server.protocol import MSG_TYPES, ProtocolError


async def authenticate(websocket, repo):
    async for raw in websocket:
        try:
            msg = protocol.decode(raw)
        except ProtocolError:
            continue

        username = msg.get('username')
        password = msg.get('password')
        if msg['type'] == MSG_TYPES['REGISTER'] and username and password:
            ok = repo.register(username, password)
        elif msg['type'] == MSG_TYPES['LOGIN'] and username and password:
            ok = repo.authenticate(username, password)
        else:
            ok = False

        if ok:
            conn = PlayerConnection(websocket, username, repo.get_rating(username))
            await conn.send({'type': MSG_TYPES['OK']})
            return conn
        await websocket.send(protocol.encode(MSG_TYPES['ERROR'], message='login failed'))
    return None

import protocol


class PlayerConnection:
    def __init__(self, websocket, username, rating):
        self.websocket = websocket
        self.username = username
        self.rating = rating
        self.room_id = None

    async def send(self, message):
        await self.websocket.send(protocol.encode_message(message))

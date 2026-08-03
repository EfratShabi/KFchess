import protocol

ROOM_OWNER_KEY = 'room:{room_id}:owner'
ROOM_EPOCH_KEY = 'room:{room_id}:epoch'
ROOM_SNAPSHOT_KEY = 'room:{room_id}:snapshot'
ROOM_PLAYERS_KEY = 'room:{room_id}:players'

LEASE_TTL_SECONDS = 5


class RoomState:
    def __init__(self, redis_client, lease_ttl_seconds=LEASE_TTL_SECONDS):
        self.redis = redis_client
        self.lease_ttl_seconds = lease_ttl_seconds

    async def claim_room(self, room_id, shard_id):
        new_epoch = await self.redis.incr(ROOM_EPOCH_KEY.format(room_id=room_id))
        await self.redis.set(
            ROOM_OWNER_KEY.format(room_id=room_id), shard_id, ex=self.lease_ttl_seconds)
        return new_epoch

    async def renew_lease(self, room_id):
        await self.redis.expire(ROOM_OWNER_KEY.format(room_id=room_id), self.lease_ttl_seconds)

    async def get_epoch(self, room_id):
        value = await self.redis.get(ROOM_EPOCH_KEY.format(room_id=room_id))
        return int(value) if value is not None else None

    async def find_orphaned_rooms(self):
        orphaned = []
        async for key in self.redis.scan_iter(match=ROOM_SNAPSHOT_KEY.format(room_id='*')):
            room_id = key.split(':')[1]
            if not await self.redis.exists(ROOM_OWNER_KEY.format(room_id=room_id)):
                orphaned.append(room_id)
        return orphaned

    async def save_snapshot(self, room_id, snapshot):
        await self.redis.set(ROOM_SNAPSHOT_KEY.format(room_id=room_id), protocol.encode_message(snapshot))

    async def get_snapshot(self, room_id):
        raw = await self.redis.get(ROOM_SNAPSHOT_KEY.format(room_id=room_id))
        return protocol.decode_message(raw) if raw is not None else None

    async def save_players(self, room_id, white_username, black_username):
        await self.redis.hset(
            ROOM_PLAYERS_KEY.format(room_id=room_id),
            mapping={'white': white_username, 'black': black_username},
        )

    async def get_players(self, room_id):
        data = await self.redis.hgetall(ROOM_PLAYERS_KEY.format(room_id=room_id))
        return (data['white'], data['black']) if data else None

    async def clear_room(self, room_id):
        await self.redis.delete(
            ROOM_OWNER_KEY.format(room_id=room_id),
            ROOM_EPOCH_KEY.format(room_id=room_id),
            ROOM_SNAPSHOT_KEY.format(room_id=room_id),
            ROOM_PLAYERS_KEY.format(room_id=room_id),
        )

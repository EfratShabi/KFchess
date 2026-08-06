REDIS_QUEUE_KEY = 'matchmaking:queue'
REDIS_JOINED_KEY = 'matchmaking:joined'

TRY_MATCH_SCRIPT = """
local candidates = redis.call('ZRANGEBYSCORE', KEYS[1], ARGV[1] - ARGV[2], ARGV[1] + ARGV[2])
if #candidates == 0 then
    return false
end
redis.call('ZREM', KEYS[1], candidates[1])
return candidates[1]
"""


class MatchmakingQueue:
    def __init__(self, redis_client, rating_range=100, timeout_s=60):
        self.redis = redis_client
        self.rating_range = rating_range
        self.timeout_s = timeout_s
        self._try_match_script = redis_client.register_script(TRY_MATCH_SCRIPT)

    async def enqueue(self, username, rating, now):
        await self.redis.zadd(REDIS_QUEUE_KEY, {username: rating})
        await self.redis.hset(REDIS_JOINED_KEY, username, now)

    async def try_match(self, username, rating):
        matched = await self._try_match_script(keys=[REDIS_QUEUE_KEY], args=[rating, self.rating_range])
        if not matched:
            return None
        await self.redis.hdel(REDIS_JOINED_KEY, matched)
        return matched

    async def expire(self, now):
        joined = await self.redis.hgetall(REDIS_JOINED_KEY)
        expired = [username for username, joined_at in joined.items() if now - float(joined_at) >= self.timeout_s]
        if expired:
            await self.redis.zrem(REDIS_QUEUE_KEY, *expired)
            await self.redis.hdel(REDIS_JOINED_KEY, *expired)
        return expired

import asyncio

from server.session.matchmaking import MatchmakingQueue


def test_try_match_on_empty_queue_returns_none(redis_client):
    queue = MatchmakingQueue(redis_client)

    assert asyncio.run(queue.try_match('conn_b', 1200)) is None


def test_try_match_finds_waiting_player_within_range(redis_client):
    queue = MatchmakingQueue(redis_client, rating_range=100)

    async def scenario():
        await queue.enqueue('conn_a', 1200, now=0)
        return await queue.try_match('conn_b', 1250)

    assert asyncio.run(scenario()) == 'conn_a'


def test_matched_player_is_removed_from_the_queue(redis_client):
    queue = MatchmakingQueue(redis_client, rating_range=100)

    async def scenario():
        await queue.enqueue('conn_a', 1200, now=0)
        await queue.try_match('conn_b', 1250)
        return await queue.try_match('conn_c', 1250)

    assert asyncio.run(scenario()) is None


def test_try_match_rejects_player_outside_rating_range(redis_client):
    queue = MatchmakingQueue(redis_client, rating_range=100)

    async def scenario():
        await queue.enqueue('conn_a', 1200, now=0)
        return await queue.try_match('conn_b', 1400)

    assert asyncio.run(scenario()) is None


def test_try_match_prefers_earliest_joined_player_in_range(redis_client):
    queue = MatchmakingQueue(redis_client, rating_range=100)

    async def scenario():
        await queue.enqueue('conn_a', 1200, now=0)
        await queue.enqueue('conn_b', 1220, now=1)
        return await queue.try_match('conn_c', 1210)

    assert asyncio.run(scenario()) == 'conn_a'


def test_expire_removes_players_past_timeout(redis_client):
    queue = MatchmakingQueue(redis_client, timeout_s=60)

    async def scenario():
        await queue.enqueue('conn_a', 1200, now=0)
        expired = await queue.expire(now=60)
        match = await queue.try_match('conn_b', 1200)
        return expired, match

    expired, match = asyncio.run(scenario())
    assert expired == ['conn_a']
    assert match is None


def test_expire_keeps_players_under_timeout(redis_client):
    queue = MatchmakingQueue(redis_client, timeout_s=60)

    async def scenario():
        await queue.enqueue('conn_a', 1200, now=0)
        expired = await queue.expire(now=59)
        match = await queue.try_match('conn_b', 1200)
        return expired, match

    expired, match = asyncio.run(scenario())
    assert expired == []
    assert match is not None


def test_expire_does_not_remove_players_still_within_range_of_a_later_match(redis_client):
    queue = MatchmakingQueue(redis_client, timeout_s=60)

    async def scenario():
        await queue.enqueue('conn_a', 1200, now=0)
        await queue.enqueue('conn_b', 1200, now=30)
        await queue.expire(now=60)
        return await queue.try_match('conn_c', 1200)

    assert asyncio.run(scenario()) == 'conn_b'

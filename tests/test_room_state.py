import asyncio

import protocol
from protocol import Snapshot
from server.room_state import RoomState, ROOM_EPOCH_KEY, ROOM_OWNER_KEY, ROOM_SNAPSHOT_KEY


def test_claim_room_starts_at_epoch_one(redis_client):
    store = RoomState(redis_client)

    async def scenario():
        return await store.claim_room('room1', 'shard-a')

    assert asyncio.run(scenario()) == 1


def test_claim_room_increments_epoch_on_reclaim(redis_client):
    store = RoomState(redis_client)

    async def scenario():
        first = await store.claim_room('room1', 'shard-a')
        second = await store.claim_room('room1', 'shard-b')
        return first, second

    first, second = asyncio.run(scenario())
    assert first == 1
    assert second == 2


def test_concurrent_claims_get_distinct_epochs(redis_client):
    store = RoomState(redis_client)

    async def scenario():
        return await asyncio.gather(
            store.claim_room('room1', 'shard-a'),
            store.claim_room('room1', 'shard-b'),
        )

    epochs = asyncio.run(scenario())
    assert sorted(epochs) == [1, 2]


def test_renew_lease_extends_ttl(redis_client):
    store = RoomState(redis_client, lease_ttl_seconds=100)

    async def scenario():
        await store.claim_room('room1', 'shard-a')
        await store.renew_lease('room1')
        return await redis_client.ttl(ROOM_OWNER_KEY.format(room_id='room1'))

    ttl = asyncio.run(scenario())
    assert 90 < ttl <= 100


def test_epoch_key_has_no_ttl(redis_client):
    store = RoomState(redis_client)

    async def scenario():
        await store.claim_room('room1', 'shard-a')
        return await redis_client.ttl(ROOM_EPOCH_KEY.format(room_id='room1'))

    assert asyncio.run(scenario()) == -1


def test_save_and_read_back_snapshot(redis_client):
    store = RoomState(redis_client)
    snapshot = Snapshot(pieces={}, scores={'w': 0, 'b': 0}, game_over=False)

    async def scenario():
        await store.save_snapshot('room1', snapshot)
        return await redis_client.get(ROOM_SNAPSHOT_KEY.format(room_id='room1'))

    raw = asyncio.run(scenario())
    restored = protocol.decode_message(raw)
    assert restored == snapshot


def test_clear_room_removes_all_three_keys(redis_client):
    store = RoomState(redis_client)
    snapshot = Snapshot(pieces={}, scores={'w': 0, 'b': 0}, game_over=False)

    async def scenario():
        await store.claim_room('room1', 'shard-a')
        await store.save_snapshot('room1', snapshot)
        await store.clear_room('room1')
        return await asyncio.gather(
            redis_client.exists(ROOM_OWNER_KEY.format(room_id='room1')),
            redis_client.exists(ROOM_EPOCH_KEY.format(room_id='room1')),
            redis_client.exists(ROOM_SNAPSHOT_KEY.format(room_id='room1')),
        )

    owner_exists, epoch_exists, snapshot_exists = asyncio.run(scenario())
    assert owner_exists == 0
    assert epoch_exists == 0
    assert snapshot_exists == 0


def test_get_epoch_returns_current_value(redis_client):
    store = RoomState(redis_client)

    async def scenario():
        await store.claim_room('room1', 'shard-a')
        return await store.get_epoch('room1')

    assert asyncio.run(scenario()) == 1


def test_get_epoch_for_unknown_room_is_none(redis_client):
    store = RoomState(redis_client)

    assert asyncio.run(store.get_epoch('ghost-room')) is None


def test_find_orphaned_rooms_finds_snapshot_without_live_owner(redis_client):
    store = RoomState(redis_client)
    snapshot = Snapshot(pieces={}, scores={'w': 0, 'b': 0}, game_over=False)

    async def scenario():
        # room1: crashed mid-game -- snapshot+epoch survive, owner lease already gone
        await store.claim_room('room1', 'shard-a')
        await store.save_snapshot('room1', snapshot)
        await redis_client.delete(ROOM_OWNER_KEY.format(room_id='room1'))

        # room2: still alive -- owner lease present
        await store.claim_room('room2', 'shard-a')
        await store.save_snapshot('room2', snapshot)

        return await store.find_orphaned_rooms()

    assert asyncio.run(scenario()) == ['room1']


def test_find_orphaned_rooms_empty_when_nothing_crashed(redis_client):
    store = RoomState(redis_client)

    assert asyncio.run(store.find_orphaned_rooms()) == []


def test_get_snapshot_returns_none_when_missing(redis_client):
    store = RoomState(redis_client)

    assert asyncio.run(store.get_snapshot('ghost-room')) is None


def test_save_and_get_snapshot_round_trip(redis_client):
    store = RoomState(redis_client)
    snapshot = Snapshot(pieces={}, scores={'w': 0, 'b': 0}, game_over=False)

    async def scenario():
        await store.save_snapshot('room1', snapshot)
        return await store.get_snapshot('room1')

    assert asyncio.run(scenario()) == snapshot


def test_save_and_get_players_round_trip(redis_client):
    store = RoomState(redis_client)

    async def scenario():
        await store.save_players('room1', 'alice', 'bob')
        return await store.get_players('room1')

    assert asyncio.run(scenario()) == ('alice', 'bob')


def test_get_players_for_unknown_room_is_none(redis_client):
    store = RoomState(redis_client)

    assert asyncio.run(store.get_players('ghost-room')) is None


def test_clear_room_removes_players_key_too(redis_client):
    store = RoomState(redis_client)

    async def scenario():
        await store.save_players('room1', 'alice', 'bob')
        await store.clear_room('room1')
        return await store.get_players('room1')

    assert asyncio.run(scenario()) is None

from server.session.allocator import GameAllocator, ShardInfo


def test_chooses_shard_with_fewest_active_rooms():
    candidates = [
        ShardInfo(shard_id='shard-a', active_rooms=5),
        ShardInfo(shard_id='shard-b', active_rooms=2),
    ]
    assert GameAllocator.choose_shard(candidates) == 'shard-b'


def test_single_candidate_is_chosen():
    candidates = [ShardInfo(shard_id='shard-a', active_rooms=0)]
    assert GameAllocator.choose_shard(candidates) == 'shard-a'

from server.matchmaking import MatchmakingQueue


def test_try_match_on_empty_queue_returns_none():
    queue = MatchmakingQueue()
    assert queue.try_match('conn_b', 1200) is None


def test_try_match_finds_waiting_player_within_range():
    queue = MatchmakingQueue(rating_range=100)
    queue.enqueue('conn_a', 1200, now=0)

    match = queue.try_match('conn_b', 1250)

    assert match.connection == 'conn_a'
    assert match.rating == 1200


def test_matched_player_is_removed_from_the_queue():
    queue = MatchmakingQueue(rating_range=100)
    queue.enqueue('conn_a', 1200, now=0)

    queue.try_match('conn_b', 1250)

    assert queue.try_match('conn_c', 1250) is None


def test_try_match_rejects_player_outside_rating_range():
    queue = MatchmakingQueue(rating_range=100)
    queue.enqueue('conn_a', 1200, now=0)

    assert queue.try_match('conn_b', 1400) is None


def test_try_match_prefers_earliest_joined_player_in_range():
    queue = MatchmakingQueue(rating_range=100)
    queue.enqueue('conn_a', 1200, now=0)
    queue.enqueue('conn_b', 1220, now=1)

    match = queue.try_match('conn_c', 1210)

    assert match.connection == 'conn_a'


def test_expire_removes_players_past_timeout():
    queue = MatchmakingQueue(timeout_s=60)
    queue.enqueue('conn_a', 1200, now=0)

    expired = queue.expire(now=60)

    assert [p.connection for p in expired] == ['conn_a']
    assert queue.try_match('conn_b', 1200) is None


def test_expire_keeps_players_under_timeout():
    queue = MatchmakingQueue(timeout_s=60)
    queue.enqueue('conn_a', 1200, now=0)

    expired = queue.expire(now=59)

    assert expired == []
    assert queue.try_match('conn_b', 1200) is not None


def test_expire_does_not_remove_players_still_within_range_of_a_later_match():
    queue = MatchmakingQueue(timeout_s=60)
    queue.enqueue('conn_a', 1200, now=0)
    queue.enqueue('conn_b', 1200, now=30)

    queue.expire(now=60)

    assert queue.try_match('conn_c', 1200).connection == 'conn_b'

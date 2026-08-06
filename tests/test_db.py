import pytest

from core.config.constants import WHITE_COLOR
from server.persistence.db import AccountRepository


@pytest.fixture
def repo(db_conn):
    return AccountRepository(db_conn)


def test_register_new_user_succeeds(repo):
    assert repo.register('efrat', 'secret') is True


def test_register_duplicate_username_fails(repo):
    repo.register('efrat', 'secret')
    assert repo.register('efrat', 'other-secret') is False


def test_authenticate_correct_password(repo):
    repo.register('efrat', 'secret')
    assert repo.authenticate('efrat', 'secret') is True


def test_authenticate_wrong_password(repo):
    repo.register('efrat', 'secret')
    assert repo.authenticate('efrat', 'wrong') is False


def test_authenticate_unknown_user(repo):
    assert repo.authenticate('nobody', 'secret') is False


def test_new_user_gets_default_rating(repo):
    repo.register('efrat', 'secret')
    assert repo.get_rating('efrat') == 1200


def test_get_rating_for_unknown_user_returns_none(repo):
    assert repo.get_rating('nobody') is None


def test_update_rating_changes_stored_value(repo):
    repo.register('efrat', 'secret')
    repo.update_rating('efrat', 1310)
    assert repo.get_rating('efrat') == 1310


def test_get_history_returns_most_recent_game_first(repo):
    repo.register('alice', 'secret')
    repo.save_result('room1', 'alice', 'bob', WHITE_COLOR, 1216, 1184)
    repo.save_result('room2', 'alice', 'carol', WHITE_COLOR, 1230, 1170)

    history = repo.get_history('alice')

    assert [record.room_id for record in history] == ['room2', 'room1']


def test_get_history_excludes_other_users_games(repo):
    repo.register('alice', 'secret')
    repo.save_result('room1', 'alice', 'bob', WHITE_COLOR, 1216, 1184)

    assert repo.get_history('carol') == []


def test_get_history_respects_limit(repo):
    repo.register('alice', 'secret')
    for i in range(3):
        repo.save_result(f'room{i}', 'alice', 'bob', WHITE_COLOR, 1200, 1200)

    assert len(repo.get_history('alice', limit=2)) == 2

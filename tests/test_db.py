import pytest

from server.db import init_db, AccountRepository


@pytest.fixture
def repo():
    conn = init_db(':memory:')
    return AccountRepository(conn)


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

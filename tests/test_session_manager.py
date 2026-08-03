from server.connection import PlayerConnection
from server.session import GameSession, SessionStatus
from server.session_manager import SessionManager


def make_pair():
    white = PlayerConnection(None, 'alice', 1200)
    black = PlayerConnection(None, 'bob', 1200)
    return white, black


def test_create_session_returns_a_session_with_the_players_assigned():
    manager = SessionManager()
    white, black = make_pair()

    session = manager.create_session(white, black)

    assert session.players['w'] is white
    assert session.players['b'] is black


def test_created_session_can_be_found_by_its_room_id():
    manager = SessionManager()
    white, black = make_pair()

    session = manager.create_session(white, black)

    assert manager.get(session.room_id) is session


def test_get_unknown_room_id_returns_none():
    manager = SessionManager()
    assert manager.get('no-such-room') is None


def test_two_sessions_get_different_room_ids():
    manager = SessionManager()
    white_a, black_a = make_pair()
    white_b, black_b = make_pair()

    session_a = manager.create_session(white_a, black_a)
    session_b = manager.create_session(white_b, black_b)

    assert session_a.room_id != session_b.room_id


def test_remove_makes_the_session_unfindable():
    manager = SessionManager()
    white, black = make_pair()
    session = manager.create_session(white, black)

    manager.remove(session.room_id)

    assert manager.get(session.room_id) is None


def test_remove_unknown_room_id_does_not_raise():
    manager = SessionManager()
    manager.remove('no-such-room')


def test_has_active_session_true_for_player_in_an_active_session():
    manager = SessionManager()
    white, black = make_pair()
    manager.create_session(white, black)

    assert manager.has_active_session('alice') is True
    assert manager.has_active_session('bob') is True


def test_has_active_session_false_for_unrelated_username():
    manager = SessionManager()
    white, black = make_pair()
    manager.create_session(white, black)

    assert manager.has_active_session('mallory') is False


def test_has_active_session_false_once_session_is_no_longer_active():
    manager = SessionManager()
    white, black = make_pair()
    session = manager.create_session(white, black)
    session.status = SessionStatus.FINISHED

    assert manager.has_active_session('alice') is False


def test_restore_registers_a_session_under_its_own_room_id():
    manager = SessionManager()
    white, black = make_pair()
    session = GameSession('recovered-room', white, black)

    manager.restore(session)

    assert manager.get('recovered-room') is session
    assert manager.has_active_session('alice') is True

from core.config.constants import WHITE_COLOR, BLACK_COLOR
from server.connection import PlayerConnection
from server.db import init_db, AccountRepository
from server.game_result import apply_rating_changes
from server.session import GameSession


def make_finished_session(winner_color):
    conn = init_db(':memory:')
    repo = AccountRepository(conn)
    repo.register('alice', 'secret')
    repo.register('bob', 'secret')

    white = PlayerConnection(None, 'alice', 1200)
    black = PlayerConnection(None, 'bob', 1200)
    session = GameSession('room1', white, black)
    session.state.game_over = True
    session.state.winner = winner_color

    return session, white, black, repo


def test_white_win_updates_db_ratings():
    session, white, black, repo = make_finished_session(WHITE_COLOR)

    apply_rating_changes(session, repo)

    assert repo.get_rating('alice') == 1216
    assert repo.get_rating('bob') == 1184


def test_black_win_updates_db_ratings():
    session, white, black, repo = make_finished_session(BLACK_COLOR)

    apply_rating_changes(session, repo)

    assert repo.get_rating('alice') == 1184
    assert repo.get_rating('bob') == 1216


def test_connection_rating_attribute_is_updated_too():
    session, white, black, repo = make_finished_session(WHITE_COLOR)

    apply_rating_changes(session, repo)

    assert white.rating == 1216
    assert black.rating == 1184

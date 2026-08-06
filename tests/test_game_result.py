from core.config.constants import WHITE_COLOR, BLACK_COLOR
from server.session.connection import PlayerConnection
from server.postgame.game_result import compute_rating_changes
from server.session.session import GameSession


def make_finished_session(winner_color):
    white = PlayerConnection(None, 'alice', 1200)
    black = PlayerConnection(None, 'bob', 1200)
    session = GameSession('room1', white, black)
    session.state.game_over = True
    session.state.winner = winner_color

    return session, white, black


def test_white_win_computes_correct_ratings():
    session, white, black = make_finished_session(WHITE_COLOR)

    new_white, new_black = compute_rating_changes(session)

    assert new_white == 1216
    assert new_black == 1184


def test_black_win_computes_correct_ratings():
    session, white, black = make_finished_session(BLACK_COLOR)

    new_white, new_black = compute_rating_changes(session)

    assert new_white == 1184
    assert new_black == 1216


def test_connection_rating_attribute_is_updated_too():
    session, white, black = make_finished_session(WHITE_COLOR)

    compute_rating_changes(session)

    assert white.rating == 1216
    assert black.rating == 1184

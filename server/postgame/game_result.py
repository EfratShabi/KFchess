from core.config.constants import WHITE_COLOR, BLACK_COLOR
from server.postgame.rating import update_ratings


def compute_rating_changes(session):
    white_conn = session.players[WHITE_COLOR]
    black_conn = session.players[BLACK_COLOR]
    score_white = 1 if session.service.get_winner() == WHITE_COLOR else 0
    new_white, new_black = update_ratings(white_conn.rating, black_conn.rating, score_white)
    white_conn.rating = new_white
    black_conn.rating = new_black
    return new_white, new_black

from core.config.constants import WHITE_COLOR, BLACK_COLOR
from server.rating import update_ratings


def apply_rating_changes(session, repo):
    white_conn = session.players[WHITE_COLOR]
    black_conn = session.players[BLACK_COLOR]
    white_rating = repo.get_rating(white_conn.username)
    black_rating = repo.get_rating(black_conn.username)
    score_white = 1 if session.service.get_winner() == WHITE_COLOR else 0
    new_white, new_black = update_ratings(white_rating, black_rating, score_white)
    repo.update_rating(white_conn.username, new_white)
    repo.update_rating(black_conn.username, new_black)
    white_conn.rating = new_white
    black_conn.rating = new_black

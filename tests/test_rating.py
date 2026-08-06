from server.postgame.rating import expected_score, update_ratings


def test_expected_score_is_half_for_equal_ratings():
    assert expected_score(1200, 1200) == 0.5


def test_expected_score_favors_higher_rated_player():
    assert expected_score(1600, 1200) > 0.5
    assert expected_score(1200, 1600) < 0.5


def test_equal_ratings_win_matches_worked_example():
    new_a, new_b = update_ratings(1200, 1200, score_a=1)
    assert (new_a, new_b) == (1216, 1184)


def test_equal_ratings_loss_is_symmetric_to_win():
    new_a, new_b = update_ratings(1200, 1200, score_a=0)
    assert (new_a, new_b) == (1184, 1216)


def test_draw_between_equal_ratings_leaves_both_unchanged():
    new_a, new_b = update_ratings(1200, 1200, score_a=0.5)
    assert (new_a, new_b) == (1200, 1200)


def test_favorite_winning_gains_fewer_points_than_underdog_winning():
    favorite_gain = update_ratings(1600, 1200, score_a=1)[0] - 1600
    underdog_gain = update_ratings(1200, 1600, score_a=1)[0] - 1200
    assert 0 < favorite_gain < underdog_gain


def test_rating_change_is_zero_sum():
    new_a, new_b = update_ratings(1450, 1300, score_a=1)
    gain = new_a - 1450
    loss = 1300 - new_b
    assert gain == loss

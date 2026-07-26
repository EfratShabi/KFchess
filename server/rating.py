K_FACTOR = 32
RATING_SCALE = 400


def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / RATING_SCALE))


def update_ratings(rating_a, rating_b, score_a):
    expected_a = expected_score(rating_a, rating_b)
    expected_b = 1 - expected_a
    score_b = 1 - score_a
    new_a = round(rating_a + K_FACTOR * (score_a - expected_a))
    new_b = round(rating_b + K_FACTOR * (score_b - expected_b))
    return new_a, new_b

# -*- coding: utf-8 -*-
"""
טסטים ל-Jump class
"""
from core.domain.jump import Jump
from core.domain.movement import Movement


# ---------- intercepts ----------

def test_intercepts_true_when_enemy_move_lands_on_the_jump_cell():
    jump = Jump('wK', (1, 1), arrival_time=1000)
    enemy_move = Movement('bR', (0, 0), (1, 1), start_time=0, arrival_time=800)
    assert jump.intercepts(enemy_move) is True


def test_intercepts_false_when_move_lands_on_a_different_cell():
    jump = Jump('wK', (1, 1), arrival_time=1000)
    move_elsewhere = Movement('bR', (0, 0), (2, 2), start_time=0, arrival_time=800)
    assert jump.intercepts(move_elsewhere) is False


def test_intercepts_false_when_move_belongs_to_the_same_color():
    # קפיצה של כלי לבן לא "תופסת" מהלך של כלי לבן אחר שנוחת שם
    jump = Jump('wK', (1, 1), arrival_time=1000)
    friendly_move = Movement('wR', (0, 0), (1, 1), start_time=0, arrival_time=800)
    assert jump.intercepts(friendly_move) is False

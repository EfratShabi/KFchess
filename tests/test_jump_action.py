# -*- coding: utf-8 -*-
"""
טסטים ל-Jump class
"""
from core.domain.jump import Jump
from core.domain.movement import Movement


# ---------- is_expired ----------

def test_is_expired_false_before_landing_time():
    jump = Jump('wK', (1, 1), arrival_time=1000)
    assert jump.is_expired(999) is False


def test_is_expired_false_exactly_at_landing_time():
    # ב-Jump ה"תפיסה" תקפה עד וכולל arrival_time - רק זמן מאוחר יותר פוקע
    jump = Jump('wK', (1, 1), arrival_time=1000)
    assert jump.is_expired(1000) is False


def test_is_expired_true_after_landing_time():
    jump = Jump('wK', (1, 1), arrival_time=1000)
    assert jump.is_expired(1001) is True


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

# -*- coding: utf-8 -*-
"""טסטים ל-Movement ו-Jump"""
from core.domain.movement import Movement
from core.domain.jump import Jump


# ──────────────────────────────
# Movement.is_due
# ──────────────────────────────

def test_movement_not_due_before_arrival():
    m = Movement('wR', (0, 0), (0, 2), start_time=0, arrival_time=2000)
    assert m.is_due(1999) is False

def test_movement_due_exactly_at_arrival():
    m = Movement('wR', (0, 0), (0, 2), start_time=0, arrival_time=2000)
    assert m.is_due(2000) is True

def test_movement_due_after_arrival():
    m = Movement('wR', (0, 0), (0, 2), start_time=0, arrival_time=2000)
    assert m.is_due(3000) is True

def test_movement_stores_piece():
    m = Movement('bK', (1, 1), (2, 2), start_time=0, arrival_time=1000)
    assert m.piece == 'bK'

def test_movement_stores_start_end():
    m = Movement('wN', (0, 0), (2, 1), start_time=0, arrival_time=500)
    assert m.start == (0, 0)
    assert m.end == (2, 1)


# ──────────────────────────────
# Jump.is_expired
# ──────────────────────────────

def test_jump_not_expired_before_landing():
    j = Jump('wK', (1, 1), arrival_time=1000)
    assert j.is_expired(999) is False

def test_jump_not_expired_exactly_at_landing():
    j = Jump('wK', (1, 1), arrival_time=1000)
    assert j.is_expired(1000) is False

def test_jump_expired_after_landing():
    j = Jump('wK', (1, 1), arrival_time=1000)
    assert j.is_expired(1001) is True


# ──────────────────────────────
# Jump.intercepts
# ──────────────────────────────

def test_intercepts_enemy_on_same_cell():
    j = Jump('wK', (1, 1), arrival_time=1000)
    m = Movement('bR', (0, 0), (1, 1), start_time=0, arrival_time=800)
    assert j.intercepts(m) is True

def test_intercepts_false_different_cell():
    j = Jump('wK', (1, 1), arrival_time=1000)
    m = Movement('bR', (0, 0), (2, 2), start_time=0, arrival_time=800)
    assert j.intercepts(m) is False

def test_intercepts_false_same_color():
    j = Jump('wK', (1, 1), arrival_time=1000)
    m = Movement('wR', (0, 0), (1, 1), start_time=0, arrival_time=800)
    assert j.intercepts(m) is False

def test_intercepts_false_enemy_lands_elsewhere():
    j = Jump('wK', (1, 1), arrival_time=1000)
    m = Movement('bR', (0, 0), (0, 3), start_time=0, arrival_time=800)
    assert j.intercepts(m) is False

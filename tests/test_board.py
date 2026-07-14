# -*- coding: utf-8 -*-
"""טסטים ל-Board — כל מתודות המחלקה"""
from core.domain.board import Board, EMPTY_CELL


def grid(*rows):
    return [r.split() for r in rows]


# ──────────────────────────────
# __init__ — מימדים
# ──────────────────────────────

def test_board_rows_count():
    b = Board(grid("wR . .", ". . ."))
    assert b.rows == 2

def test_board_cols_count():
    b = Board(grid("wR . ."))
    assert b.cols == 3

def test_board_single_row():
    b = Board(grid("wK bK ."))
    assert b.rows == 1
    assert b.cols == 3


# ──────────────────────────────
# is_empty
# ──────────────────────────────

def test_is_empty_true_for_dot():
    b = Board(grid(". . ."))
    assert b.is_empty(0, 1) is True

def test_is_empty_false_for_piece():
    b = Board(grid("wR . ."))
    assert b.is_empty(0, 0) is False

def test_is_empty_true_after_clear():
    b = Board(grid("wR . ."))
    b.clear_cell(0, 0)
    assert b.is_empty(0, 0) is True


# ──────────────────────────────
# get_piece_color / get_piece_kind / get_piece_str
# ──────────────────────────────

def test_get_piece_color_white():
    b = Board(grid("wR . ."))
    assert b.get_piece_color(0, 0) == 'w'

def test_get_piece_color_black():
    b = Board(grid("bK . ."))
    assert b.get_piece_color(0, 0) == 'b'

def test_get_piece_color_empty_returns_none():
    b = Board(grid(". . ."))
    assert b.get_piece_color(0, 0) is None

def test_get_piece_kind_rook():
    b = Board(grid("wR . ."))
    assert b.get_piece_kind(0, 0) == 'R'

def test_get_piece_kind_empty_returns_none():
    b = Board(grid(". . ."))
    assert b.get_piece_kind(0, 0) is None

def test_get_piece_str_returns_full_token():
    b = Board(grid("bQ . ."))
    assert b.get_piece_str(0, 0) == 'bQ'

def test_get_piece_str_empty_returns_none():
    b = Board(grid(". . ."))
    assert b.get_piece_str(0, 0) is None


# ──────────────────────────────
# set_piece / clear_cell
# ──────────────────────────────

def test_set_piece_places_token():
    b = Board(grid(". . ."))
    b.set_piece(0, 1, 'wN')
    assert b.grid[0][1] == 'wN'

def test_clear_cell_places_dot():
    b = Board(grid("wR . ."))
    b.clear_cell(0, 0)
    assert b.grid[0][0] == EMPTY_CELL


# ──────────────────────────────
# is_in_bounds
# ──────────────────────────────

def test_in_bounds_top_left():
    b = Board(grid(". . .", ". . ."))
    assert b.is_in_bounds(0, 0) is True

def test_in_bounds_bottom_right():
    b = Board(grid(". . .", ". . ."))
    assert b.is_in_bounds(1, 2) is True

def test_out_of_bounds_negative_row():
    b = Board(grid(". . ."))
    assert b.is_in_bounds(-1, 0) is False

def test_out_of_bounds_negative_col():
    b = Board(grid(". . ."))
    assert b.is_in_bounds(0, -1) is False

def test_out_of_bounds_row_too_large():
    b = Board(grid(". . ."))
    assert b.is_in_bounds(1, 0) is False

def test_out_of_bounds_col_too_large():
    b = Board(grid(". . ."))
    assert b.is_in_bounds(0, 3) is False


# ──────────────────────────────
# __str__ — פלט טקסטואלי
# ──────────────────────────────

def test_str_single_row():
    b = Board(grid("wR . bK"))
    assert str(b) == "wR . bK"

def test_str_two_rows():
    b = Board(grid("wR . .", ". bK ."))
    assert str(b) == "wR . .\n. bK ."

def test_str_all_empty():
    b = Board(grid(". . .", ". . ."))
    assert str(b) == ". . .\n. . ."

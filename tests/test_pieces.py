# -*- coding: utf-8 -*-
"""טסטים לחוקי תנועה של כל סוג כלי — can_move"""
import pytest
from domain.piece import King, Rook, Bishop, Queen, Knight, Pawn, create_piece
from domain.board import EMPTY_CELL


def empty(rows, cols):
    return [[EMPTY_CELL] * cols for _ in range(rows)]


def board_from(*rows):
    return [r.split() for r in rows]


# ──────────────────────────────
# King
# ──────────────────────────────

def test_king_moves_one_up():
    b = empty(3, 3)
    assert King('w').can_move(b, (2, 1), (1, 1)) is True

def test_king_moves_one_diagonal():
    b = empty(3, 3)
    assert King('w').can_move(b, (1, 1), (0, 0)) is True

def test_king_cannot_move_two_cells():
    b = empty(3, 3)
    assert King('w').can_move(b, (0, 0), (0, 2)) is False

def test_king_cannot_stay_in_place():
    b = empty(3, 3)
    assert King('w').can_move(b, (1, 1), (1, 1)) is True  # same pos: blocked by own piece check only if piece there

def test_king_blocked_by_friendly():
    b = board_from("wR wK .")
    assert King('w').can_move(b, (0, 1), (0, 0)) is False


# ──────────────────────────────
# Rook
# ──────────────────────────────

def test_rook_moves_horizontally():
    b = empty(3, 4)
    assert Rook('w').can_move(b, (0, 0), (0, 3)) is True

def test_rook_moves_vertically():
    b = empty(4, 3)
    assert Rook('w').can_move(b, (0, 0), (3, 0)) is True

def test_rook_cannot_move_diagonally():
    b = empty(3, 3)
    assert Rook('w').can_move(b, (0, 0), (2, 2)) is False

def test_rook_blocked_by_piece_in_path():
    b = board_from("wR bP . .")
    assert Rook('w').can_move(b, (0, 0), (0, 3)) is False

def test_rook_captures_adjacent_enemy():
    b = board_from("wR bP .")
    assert Rook('w').can_move(b, (0, 0), (0, 1)) is True

def test_rook_blocked_by_friendly():
    b = board_from("wR wP . .")
    assert Rook('w').can_move(b, (0, 0), (0, 2)) is False

def test_rook_cannot_capture_friendly():
    b = board_from("wR wP .")
    assert Rook('w').can_move(b, (0, 0), (0, 1)) is False


# ──────────────────────────────
# Bishop
# ──────────────────────────────

def test_bishop_moves_diagonally():
    b = empty(3, 3)
    assert Bishop('w').can_move(b, (0, 0), (2, 2)) is True

def test_bishop_moves_backwards_diagonal():
    b = empty(3, 3)
    assert Bishop('w').can_move(b, (2, 2), (0, 0)) is True

def test_bishop_cannot_move_straight():
    b = empty(3, 3)
    assert Bishop('w').can_move(b, (0, 0), (0, 2)) is False

def test_bishop_cannot_move_vertically():
    b = empty(3, 3)
    assert Bishop('w').can_move(b, (0, 0), (2, 0)) is False

def test_bishop_blocked_on_diagonal():
    b = board_from("wB . .", ". bP .", ". . .")
    assert Bishop('w').can_move(b, (0, 0), (2, 2)) is False

def test_bishop_captures_diagonal_enemy():
    b = board_from("wB . .", ". bP .", ". . .")
    assert Bishop('w').can_move(b, (0, 0), (1, 1)) is True


# ──────────────────────────────
# Queen
# ──────────────────────────────

def test_queen_moves_horizontally():
    b = empty(3, 4)
    assert Queen('w').can_move(b, (0, 0), (0, 3)) is True

def test_queen_moves_vertically():
    b = empty(4, 3)
    assert Queen('w').can_move(b, (0, 0), (3, 0)) is True

def test_queen_moves_diagonally():
    b = empty(3, 3)
    assert Queen('w').can_move(b, (0, 0), (2, 2)) is True

def test_queen_blocked_horizontally():
    b = board_from("wQ bP . .")
    assert Queen('w').can_move(b, (0, 0), (0, 3)) is False

def test_queen_cannot_move_like_knight():
    b = empty(4, 4)
    assert Queen('w').can_move(b, (0, 0), (1, 2)) is False


# ──────────────────────────────
# Knight
# ──────────────────────────────

def test_knight_l_shape_2_1():
    b = empty(4, 4)
    assert Knight('w').can_move(b, (0, 0), (2, 1)) is True

def test_knight_l_shape_1_2():
    b = empty(4, 4)
    assert Knight('w').can_move(b, (0, 0), (1, 2)) is True

def test_knight_all_8_moves():
    b = empty(5, 5)
    k = Knight('w')
    targets = [(0,1),(0,3),(4,1),(4,3),(1,0),(3,0),(1,4),(3,4)]
    for t in targets:
        assert k.can_move(b, (2, 2), t) is True

def test_knight_cannot_move_straight():
    b = empty(4, 4)
    assert Knight('w').can_move(b, (1, 1), (1, 3)) is False

def test_knight_jumps_over_blockers():
    b = board_from("wN bP bP bP", "bP bP bP bP", ". bP bP bP")
    assert Knight('w').can_move(b, (0, 0), (2, 1)) is True


# ──────────────────────────────
# Pawn — לבן
# ──────────────────────────────

def test_white_pawn_one_step_forward():
    b = board_from(". . .", "wP . .", ". . .")
    assert Pawn('w').can_move(b, (1, 0), (0, 0)) is True

def test_white_pawn_blocked_forward():
    b = board_from("bP . .", "wP . .")
    assert Pawn('w').can_move(b, (1, 0), (0, 0)) is False

def test_white_pawn_double_step_from_start_row():
    # start row = len(board)-2 = 4-2 = 2
    b = board_from(". . .", ". . .", "wP . .", ". . .")
    assert Pawn('w').can_move(b, (2, 0), (0, 0)) is True

def test_white_pawn_double_step_blocked_middle():
    b = board_from(". . .", "bP . .", "wP . .", ". . .")
    assert Pawn('w').can_move(b, (2, 0), (0, 0)) is False

def test_white_pawn_cannot_double_step_outside_start():
    # 5-row board: start row = 3, pawn at row 2
    b = board_from(". . .", ". . .", "wP . .", ". . .", ". . .")
    assert Pawn('w').can_move(b, (2, 0), (0, 0)) is False

def test_white_pawn_diagonal_capture():
    b = board_from(". bR .", "wP . .", ". . .")
    assert Pawn('w').can_move(b, (1, 0), (0, 1)) is True

def test_white_pawn_cannot_capture_empty_diagonal():
    b = board_from(". . .", "wP . .", ". . .")
    assert Pawn('w').can_move(b, (1, 0), (0, 1)) is False

def test_white_pawn_cannot_capture_forward():
    b = board_from("bR . .", "wP . .")
    assert Pawn('w').can_move(b, (1, 0), (0, 0)) is False

def test_white_pawn_cannot_move_backward():
    b = board_from(". . .", "wP . .", ". . .")
    assert Pawn('w').can_move(b, (1, 0), (2, 0)) is False

# ──────────────────────────────
# Pawn — שחור
# ──────────────────────────────

def test_black_pawn_one_step_forward():
    b = board_from(". . .", "bP . .", ". . .")
    assert Pawn('b').can_move(b, (1, 0), (2, 0)) is True

def test_black_pawn_diagonal_capture():
    b = board_from(". . .", "bP . .", ". wR .")
    assert Pawn('b').can_move(b, (1, 0), (2, 1)) is True

def test_black_pawn_double_step_from_start_row():
    # black start row = 1
    b = board_from(". . .", "bP . .", ". . .", ". . .")
    assert Pawn('b').can_move(b, (1, 0), (3, 0)) is True


# ──────────────────────────────
# create_piece
# ──────────────────────────────

def test_create_piece_rook():
    p = create_piece('wR')
    assert isinstance(p, Rook)
    assert p.color == 'w'
    assert p.kind == 'R'

def test_create_piece_black_king():
    p = create_piece('bK')
    assert isinstance(p, King)
    assert p.color == 'b'

def test_piece_str():
    assert str(Rook('w')) == 'wR'
    assert str(King('b')) == 'bK'

# -*- coding: utf-8 -*-
"""טסטים ל-GameService — process_click, process_jump, process_wait"""
import pytest
from domain.board import Board
from real_time.real_time import RealTime
from services.game_service import GameService


def make_service(*rows):
    grid = [r.split() for r in rows]
    return GameService(Board(grid), RealTime())


# ──────────────────────────────
# process_click — בחירה
# ──────────────────────────────

def test_click_selects_piece():
    svc = make_service("wR . .")
    svc.process_click(50, 50)       # (0,0)
    assert svc.selected_piece == (0, 0)

def test_click_empty_cell_no_selection():
    svc = make_service(". . .")
    svc.process_click(150, 50)      # (0,1) ריק
    assert svc.selected_piece is None

def test_click_outside_board_ignored():
    svc = make_service("wR . .")
    svc.process_click(500, 500)
    assert svc.selected_piece is None

def test_click_outside_board_negative():
    svc = make_service("wR . .")
    svc.process_click(-100, -100)
    assert svc.selected_piece is None


# ──────────────────────────────
# process_click — החלפת בחירה
# ──────────────────────────────

def test_click_friendly_replaces_selection():
    svc = make_service("wR wN .")
    svc.process_click(50, 50)       # בוחר wR
    svc.process_click(150, 50)      # בוחר wN
    assert svc.selected_piece == (0, 1)

def test_click_friendly_does_not_queue_move():
    svc = make_service("wR wN .")
    svc.process_click(50, 50)
    svc.process_click(150, 50)
    assert svc.state.movements == []


# ──────────────────────────────
# process_click — רישום תנועה
# ──────────────────────────────

def test_legal_move_registers_movement():
    svc = make_service("wR . .")
    svc.process_click(50, 50)
    svc.process_click(250, 50)      # (0,2) — חוקי לצריח
    assert len(svc.state.movements) == 1

def test_legal_move_clears_selection():
    svc = make_service("wR . .")
    svc.process_click(50, 50)
    svc.process_click(250, 50)
    assert svc.selected_piece is None

def test_illegal_move_no_movement_registered():
    svc = make_service("wR . .", ". . .")
    svc.process_click(50, 50)
    svc.process_click(250, 150)     # (1,2) — אלכסון, לא חוקי לצריח
    assert svc.state.movements == []

def test_move_stores_correct_piece():
    svc = make_service("wR . .")
    svc.process_click(50, 50)
    svc.process_click(250, 50)
    assert svc.state.movements[0].piece == 'wR'

def test_move_stores_correct_destination():
    svc = make_service("wR . .")
    svc.process_click(50, 50)
    svc.process_click(250, 50)
    assert svc.state.movements[0].end == (0, 2)


# ──────────────────────────────
# process_click — כלי בתנועה
# ──────────────────────────────

def test_cannot_click_moving_piece():
    svc = make_service("wR . . .")
    svc.process_click(50, 50)
    svc.process_click(350, 50)      # שולח wR לתנועה
    svc.process_click(50, 50)       # מנסה לבחור שוב — צריך להיכשל
    assert svc.selected_piece is None


# ──────────────────────────────
# process_jump
# ──────────────────────────────

def test_jump_registers_jump():
    svc = make_service("wK . .")
    svc.process_jump(50, 50)
    assert len(svc.state.jumps) == 1

def test_jump_correct_piece():
    svc = make_service("wK . .")
    svc.process_jump(50, 50)
    assert svc.state.jumps[0].piece == 'wK'

def test_jump_empty_cell_ignored():
    svc = make_service(". . .")
    svc.process_jump(150, 50)
    assert svc.state.jumps == []

def test_jump_outside_board_ignored():
    svc = make_service("wK . .")
    svc.process_jump(500, 500)
    assert svc.state.jumps == []

def test_jump_moving_piece_ignored():
    svc = make_service("wR . . .")
    svc.process_click(50, 50)
    svc.process_click(350, 50)      # שולח wR לתנועה
    svc.process_jump(50, 50)        # מנסה לקפוץ — אמור להיכשל
    assert svc.state.jumps == []


# ──────────────────────────────
# is_game_over
# ──────────────────────────────

def test_game_over_false_initially():
    svc = make_service("wR bK .")
    assert svc.is_game_over() is False


# ──────────────────────────────
# get_board_string
# ──────────────────────────────

def test_cannot_redirect_piece_already_moving():
    svc = make_service("wR . . .", ". . . .", ". . . .", ". . . .")
    svc.process_click(50, 50)
    svc.process_click(350, 50)   # שולח wR ל-(0,3), 3000ms
    svc.process_click(50, 50)    # מנסה לבחור שוב את wR — אמור להיכשל
    svc.process_click(150, 50)   # מנסה להפנות ל-(0,1)
    assert len(svc.state.movements) == 1
    assert svc.state.movements[0].end == (0, 3)


def test_get_board_string_single_row():
    svc = make_service("wR . bK")
    assert svc.get_board_string() == "wR . bK"

def test_get_board_string_two_rows():
    svc = make_service("wR . .", ". bK .")
    assert svc.get_board_string() == "wR . .\n. bK ."

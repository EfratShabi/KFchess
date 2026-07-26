# -*- coding: utf-8 -*-
"""טסטים ל-GameService + InputController"""
import pytest
from core.domain.board import Board
from core.real_time.real_time import RealTime
from core.services.game_service import GameService
from interfaces.shared.input_controller import InputController


def make_service(*rows):
    grid = [r.split() for r in rows]
    board = Board(grid)
    svc = GameService(board, RealTime())
    ctrl = InputController(svc)
    return svc, ctrl


# ──────────────────────────────
# handle_click — בחירה
# ──────────────────────────────

def test_click_selects_piece():
    svc, ctrl = make_service("wR . .")
    ctrl.handle_click(50, 50)
    assert ctrl.selected_piece == (0, 0)

def test_click_empty_cell_no_selection():
    svc, ctrl = make_service(". . .")
    ctrl.handle_click(150, 50)
    assert ctrl.selected_piece is None

def test_click_outside_board_ignored():
    svc, ctrl = make_service("wR . .")
    ctrl.handle_click(500, 500)
    assert ctrl.selected_piece is None

def test_click_outside_board_negative():
    svc, ctrl = make_service("wR . .")
    ctrl.handle_click(-100, -100)
    assert ctrl.selected_piece is None


# ──────────────────────────────
# handle_click — החלפת בחירה
# ──────────────────────────────

def test_click_friendly_replaces_selection():
    svc, ctrl = make_service("wR wN .")
    ctrl.handle_click(50, 50)
    ctrl.handle_click(150, 50)
    assert ctrl.selected_piece == (0, 1)

def test_click_friendly_does_not_queue_move():
    svc, ctrl = make_service("wR wN .")
    ctrl.handle_click(50, 50)
    ctrl.handle_click(150, 50)
    assert svc.state.movements == []


# ──────────────────────────────
# handle_click — רישום תנועה
# ──────────────────────────────

def test_legal_move_registers_movement():
    svc, ctrl = make_service("wR . .")
    ctrl.handle_click(50, 50)
    ctrl.handle_click(250, 50)
    assert len(svc.state.movements) == 1

def test_legal_move_clears_selection():
    svc, ctrl = make_service("wR . .")
    ctrl.handle_click(50, 50)
    ctrl.handle_click(250, 50)
    assert ctrl.selected_piece is None

def test_illegal_move_no_movement_registered():
    svc, ctrl = make_service("wR . .", ". . .")
    ctrl.handle_click(50, 50)
    ctrl.handle_click(250, 150)
    assert svc.state.movements == []

def test_move_stores_correct_piece():
    svc, ctrl = make_service("wR . .")
    ctrl.handle_click(50, 50)
    ctrl.handle_click(250, 50)
    assert svc.state.movements[0].piece == 'wR'

def test_move_stores_correct_destination():
    svc, ctrl = make_service("wR . .")
    ctrl.handle_click(50, 50)
    ctrl.handle_click(250, 50)
    assert svc.state.movements[0].end == (0, 2)


# ──────────────────────────────
# handle_click — כלי בתנועה
# ──────────────────────────────

def test_cannot_click_moving_piece():
    svc, ctrl = make_service("wR . . .")
    ctrl.handle_click(50, 50)
    ctrl.handle_click(350, 50)
    ctrl.handle_click(50, 50)
    assert ctrl.selected_piece is None


# ──────────────────────────────
# handle_jump
# ──────────────────────────────

def test_jump_registers_jump():
    svc, ctrl = make_service("wK . .")
    ctrl.handle_jump(50, 50)
    assert len(svc.state.jumps) == 1

def test_jump_correct_piece():
    svc, ctrl = make_service("wK . .")
    ctrl.handle_jump(50, 50)
    assert svc.state.jumps[0].piece == 'wK'

def test_jump_empty_cell_ignored():
    svc, ctrl = make_service(". . .")
    ctrl.handle_jump(150, 50)
    assert svc.state.jumps == []

def test_jump_outside_board_ignored():
    svc, ctrl = make_service("wK . .")
    ctrl.handle_jump(500, 500)
    assert svc.state.jumps == []

def test_jump_moving_piece_ignored():
    svc, ctrl = make_service("wR . . .")
    ctrl.handle_click(50, 50)
    ctrl.handle_click(350, 50)
    ctrl.handle_jump(50, 50)
    assert svc.state.jumps == []


# ──────────────────────────────
# is_game_over
# ──────────────────────────────

def test_game_over_false_initially():
    svc, ctrl = make_service("wR bK .")
    assert svc.is_game_over() is False


# ──────────────────────────────
# get_board_string
# ──────────────────────────────

def test_cannot_redirect_piece_already_moving():
    svc, ctrl = make_service("wR . . .", ". . . .", ". . . .", ". . . .")
    ctrl.handle_click(50, 50)
    ctrl.handle_click(350, 50)
    ctrl.handle_click(50, 50)
    ctrl.handle_click(150, 50)
    assert len(svc.state.movements) == 1
    assert svc.state.movements[0].end == (0, 3)


def test_get_board_string_single_row():
    svc, ctrl = make_service("wR . bK")
    assert svc.get_board_string() == "wR . bK"

def test_get_board_string_two_rows():
    svc, ctrl = make_service("wR . .", ". bK .")
    assert svc.get_board_string() == "wR . .\n. bK ."


# ──────────────────────────────
# get_winner
# ──────────────────────────────

def test_get_winner_is_none_before_game_over():
    svc, ctrl = make_service("wR . bK")
    assert svc.get_winner() is None


def test_get_winner_returns_capturing_color_when_move_captures_king():
    svc, ctrl = make_service("wR . bK")
    assert svc.try_move((0, 0), (0, 2)) is True
    svc.process_wait(3000)
    assert svc.is_game_over() is True
    assert svc.get_winner() == 'w'


def test_get_winner_returns_capturing_color_on_midair_capture():
    svc, ctrl = make_service("bK wR .")
    assert svc.try_move((0, 0), (0, 1)) is True
    assert svc.try_jump(0, 1) is True
    svc.process_wait(1000)
    assert svc.is_game_over() is True
    assert svc.get_winner() == 'w'

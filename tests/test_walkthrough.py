# -*- coding: utf-8 -*-
import pytest
from core.domain.board import Board
from core.real_time.real_time import RealTime
from core.services.game_service import GameService
from interfaces.shared.input_controller import InputController


def grid(*rows):
    return [r.split() for r in rows]


def make_service(*rows):
    board = Board(grid(*rows))
    state = RealTime()
    svc = GameService(board, state)
    ctrl = InputController(svc)
    return svc, ctrl


class TestSelection:
    def test_click_on_piece_selects_it(self, click_xy):
        svc, ctrl = make_service("wR . .", ".  . .", ".  . .")
        ctrl.handle_click(*click_xy(0, 0))
        assert ctrl.selected_piece == (0, 0)

    def test_click_on_empty_does_not_select(self, click_xy):
        svc, ctrl = make_service(". . .", ". . .")
        ctrl.handle_click(*click_xy(0, 0))
        assert ctrl.selected_piece is None

    def test_second_click_same_color_switches_selection(self, click_xy):
        svc, ctrl = make_service("wR wK .", ".   .  .")
        ctrl.handle_click(*click_xy(0, 0))
        assert ctrl.selected_piece == (0, 0)
        ctrl.handle_click(*click_xy(0, 1))
        assert ctrl.selected_piece == (0, 1)


class TestMovement:
    def test_rook_moves_along_row(self, click_xy):
        svc, ctrl = make_service("wR . . . .", ".  . . . .")
        ctrl.handle_click(*click_xy(0, 0))
        ctrl.handle_click(*click_xy(0, 2))
        assert svc.board.get_piece_str(0, 0) == "wR"
        svc.process_wait(2000)
        assert svc.board.get_piece_str(0, 2) == "wR"
        assert svc.board.is_empty(0, 0)

    def test_rook_blocked_by_friendly(self, click_xy):
        svc, ctrl = make_service("wR wK . .", ".   .  . .")
        ctrl.handle_click(*click_xy(0, 0))
        ctrl.handle_click(*click_xy(0, 2))
        svc.process_wait(5000)
        assert svc.board.get_piece_str(0, 0) == "wR"
        assert svc.board.get_piece_str(0, 1) == "wK"

    def test_king_moves_one_step(self, click_xy):
        svc, ctrl = make_service("wK . .", ".   . .")
        ctrl.handle_click(*click_xy(0, 0))
        ctrl.handle_click(*click_xy(1, 1))
        svc.process_wait(2000)
        assert svc.board.get_piece_str(1, 1) == "wK"

    def test_king_cannot_move_two_steps(self, click_xy):
        svc, ctrl = make_service("wK . . .", ".   . . .")
        ctrl.handle_click(*click_xy(0, 0))
        ctrl.handle_click(*click_xy(0, 2))
        svc.process_wait(5000)
        assert svc.board.get_piece_str(0, 0) == "wK"

    def test_knight_jumps_L_shape(self, click_xy):
        svc, ctrl = make_service("wN . . .", ".   . . .", ".   . . .")
        ctrl.handle_click(*click_xy(0, 0))
        ctrl.handle_click(*click_xy(2, 1))
        svc.process_wait(3000)
        assert svc.board.get_piece_str(2, 1) == "wN"


class TestCapture:
    def test_rook_captures_enemy(self, click_xy):
        svc, ctrl = make_service("wR . bK .", ".   . .  .")
        ctrl.handle_click(*click_xy(0, 0))
        ctrl.handle_click(*click_xy(0, 2))
        svc.process_wait(3000)
        assert svc.board.get_piece_str(0, 2) == "wR"
        assert svc.board.is_empty(0, 0)

    def test_cannot_capture_same_color(self, click_xy):
        svc, ctrl = make_service("wR . wK .", ".   . .  .")
        ctrl.handle_click(*click_xy(0, 0))
        ctrl.handle_click(*click_xy(0, 2))
        svc.process_wait(3000)
        assert svc.board.get_piece_str(0, 0) == "wR"
        assert svc.board.get_piece_str(0, 2) == "wK"


class TestJump:
    def test_jump_removes_piece_after_duration(self, click_xy):
        svc, ctrl = make_service("wR . .", ".   . .")
        ctrl.handle_jump(*click_xy(0, 0))
        assert not svc.board.is_empty(0, 0)
        assert svc.state.is_jumping(0, 0)
        svc.process_wait(1000)
        assert not svc.state.is_jumping(0, 0)

    def test_moving_piece_captured_by_jumping_piece(self, click_xy):
        svc, ctrl = make_service("wR . bR .", ".   . .  .")
        ctrl.handle_jump(*click_xy(0, 2))
        assert svc.state.is_jumping(0, 2)
        ctrl.handle_click(*click_xy(0, 0))
        ctrl.handle_click(*click_xy(0, 2))
        svc.process_wait(2000)
        assert svc.board.is_empty(0, 0)


class TestRealTimeFlow:
    def test_two_pieces_move_simultaneously(self, click_xy):
        svc, ctrl = make_service("wR . . . bR", ".   . . . . ")
        ctrl.handle_click(*click_xy(0, 0))
        ctrl.handle_click(*click_xy(0, 1))
        ctrl.handle_click(*click_xy(0, 4))
        ctrl.handle_click(*click_xy(0, 3))
        svc.process_wait(1000)
        assert svc.board.get_piece_str(0, 1) == "wR"
        assert svc.board.get_piece_str(0, 3) == "bR"

    def test_piece_blocked_while_in_flight(self, click_xy):
        svc, ctrl = make_service("wR wK . .", ".   .  . .")
        ctrl.handle_click(*click_xy(0, 0))
        ctrl.handle_click(*click_xy(0, 1))
        svc.process_wait(2000)
        assert svc.board.get_piece_str(0, 0) == "wR"
        assert svc.board.get_piece_str(0, 1) == "wK"

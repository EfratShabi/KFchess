# -*- coding: utf-8 -*-
"""fixtures משותפים לכל הטסטים"""
import pytest
from domain.board import Board
from real_time.real_time import RealTime
from services.game_service import GameService


def grid(*rows):
    """המרת שורות ASCII ל-grid של רשימות."""
    return [r.split() for r in rows]


@pytest.fixture
def make_board():
    """מחזיר Board מוכן לשימוש."""
    def _make(*rows):
        return Board(grid(*rows))
    return _make


@pytest.fixture
def make_service():
    """מחזיר GameService מוכן לשימוש."""
    def _make(*rows):
        board = Board(grid(*rows))
        state = RealTime()
        return GameService(board, state)
    return _make

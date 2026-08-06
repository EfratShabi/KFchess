# -*- coding: utf-8 -*-
"""fixtures משותפים לכל הטסטים"""
import redis as redis_sync
import pytest
from redis.asyncio import Redis

from core.domain.board import Board
from core.real_time.real_time import RealTime
from core.services.game_service import GameService
from interfaces.shared.graphics_constants import BOARD_OFFSET_X, BOARD_OFFSET_Y, CELL_SIZE
from interfaces.shared.pixel_math import cell_to_pixel
from server.persistence.db import init_db


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


@pytest.fixture
def click_xy():
    """ממיר (row, col) לפיקסל אמצע-התא, לפי אותם קבועים גרפיים שהרנדרר האמיתי משתמש בהם."""
    def _click_xy(row, col):
        x, y = cell_to_pixel(row, col, CELL_SIZE, BOARD_OFFSET_X, BOARD_OFFSET_Y)
        return x + CELL_SIZE // 2, y + CELL_SIZE // 2
    return _click_xy


@pytest.fixture
def db_conn():
    conn = init_db()
    with conn.cursor() as cur:
        cur.execute('TRUNCATE TABLE users, results')
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def redis_client():
    redis_sync.Redis(host='localhost', port=6379).flushdb()
    return Redis(host='localhost', port=6379, decode_responses=True)

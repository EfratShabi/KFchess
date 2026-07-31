# -*- coding: utf-8 -*-
"""fixtures משותפים לכל הטסטים"""
import redis as redis_sync
import pytest
from redis.asyncio import Redis

from core.domain.board import Board
from core.real_time.real_time import RealTime
from core.services.game_service import GameService
from server.db import init_db


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
def db_conn():
    conn = init_db()
    with conn.cursor() as cur:
        cur.execute('TRUNCATE TABLE users')
    conn.commit()
    return conn


@pytest.fixture
def redis_client():
    redis_sync.Redis(host='localhost', port=6379).flushdb()
    return Redis(host='localhost', port=6379, decode_responses=True)

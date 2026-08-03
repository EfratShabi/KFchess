import os
from dataclasses import dataclass
from datetime import datetime

import psycopg2
import psycopg2.errors

from server.auth import hash_password, verify_password

DEFAULT_RATING = 1200


@dataclass
class GameRecord:
    room_id: str
    white_username: str
    black_username: str
    winner: str
    white_rating_after: int
    black_rating_after: int
    finished_at: datetime


def init_db():
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=os.environ.get('DB_PORT', '5432'),
        dbname=os.environ.get('DB_NAME', 'kfchess'),
        user=os.environ.get('DB_USER', 'kfchess'),
        password=os.environ.get('DB_PASSWORD', 'kfchess'),
    )
    with conn.cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username      TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                salt          TEXT NOT NULL,
                rating        INTEGER NOT NULL DEFAULT 1200
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id                 SERIAL PRIMARY KEY,
                room_id            TEXT NOT NULL,
                white_username     TEXT NOT NULL,
                black_username     TEXT NOT NULL,
                winner             TEXT NOT NULL,
                white_rating_after INTEGER NOT NULL,
                black_rating_after INTEGER NOT NULL,
                finished_at        TIMESTAMPTZ NOT NULL DEFAULT now()
            )
        ''')
    conn.commit()
    return conn


class AccountRepository:
    def __init__(self, conn):
        self.conn = conn

    def register(self, username, password):
        with self.conn.cursor() as cur:
            cur.execute('SELECT 1 FROM users WHERE username = %s', (username,))
            if cur.fetchone():
                self.conn.rollback()
                return False
            password_hash, salt = hash_password(password)
            try:
                cur.execute(
                    'INSERT INTO users (username, password_hash, salt, rating) VALUES (%s, %s, %s, %s)',
                    (username, password_hash, salt, DEFAULT_RATING),
                )
            except psycopg2.errors.UniqueViolation:
                self.conn.rollback()
                return False
        self.conn.commit()
        return True

    def authenticate(self, username, password):
        with self.conn.cursor() as cur:
            cur.execute('SELECT password_hash, salt FROM users WHERE username = %s', (username,))
            row = cur.fetchone()
        self.conn.commit()
        if row is None:
            return False
        password_hash, salt = row
        return verify_password(password, salt, password_hash)

    def get_rating(self, username):
        with self.conn.cursor() as cur:
            cur.execute('SELECT rating FROM users WHERE username = %s', (username,))
            row = cur.fetchone()
        self.conn.commit()
        return row[0] if row else None

    def update_rating(self, username, new_rating):
        with self.conn.cursor() as cur:
            cur.execute('UPDATE users SET rating = %s WHERE username = %s', (new_rating, username))
        self.conn.commit()

    def save_result(self, room_id, white_username, black_username, winner,
                     white_rating_after, black_rating_after):
        with self.conn.cursor() as cur:
            cur.execute(
                '''INSERT INTO results (room_id, white_username, black_username, winner,
                                         white_rating_after, black_rating_after)
                   VALUES (%s, %s, %s, %s, %s, %s)''',
                (room_id, white_username, black_username, winner,
                 white_rating_after, black_rating_after),
            )
        self.conn.commit()

    def get_history(self, username, limit=20):
        with self.conn.cursor() as cur:
            cur.execute(
                '''SELECT room_id, white_username, black_username, winner,
                          white_rating_after, black_rating_after, finished_at
                   FROM results
                   WHERE white_username = %s OR black_username = %s
                   ORDER BY finished_at DESC
                   LIMIT %s''',
                (username, username, limit),
            )
            rows = cur.fetchall()
        self.conn.commit()
        return [GameRecord(*row) for row in rows]

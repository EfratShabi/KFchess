import sqlite3

from server.auth import hash_password, verify_password

DEFAULT_RATING = 1200


def init_db(path='kfchess.db'):
    conn = sqlite3.connect(path)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username      TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            salt          TEXT NOT NULL,
            rating        INTEGER NOT NULL DEFAULT 1200
        )
    ''')
    conn.commit()
    return conn


class AccountRepository:
    def __init__(self, conn):
        self.conn = conn

    def register(self, username, password):
        if self.conn.execute('SELECT 1 FROM users WHERE username = ?', (username,)).fetchone():
            return False
        password_hash, salt = hash_password(password)
        self.conn.execute(
            'INSERT INTO users (username, password_hash, salt, rating) VALUES (?, ?, ?, ?)',
            (username, password_hash, salt, DEFAULT_RATING),
        )
        self.conn.commit()
        return True

    def authenticate(self, username, password):
        row = self.conn.execute(
            'SELECT password_hash, salt FROM users WHERE username = ?', (username,)
        ).fetchone()
        if row is None:
            return False
        password_hash, salt = row
        return verify_password(password, salt, password_hash)

    def get_rating(self, username):
        row = self.conn.execute('SELECT rating FROM users WHERE username = ?', (username,)).fetchone()
        return row[0] if row else None

    def update_rating(self, username, new_rating):
        self.conn.execute('UPDATE users SET rating = ? WHERE username = ?', (new_rating, username))
        self.conn.commit()

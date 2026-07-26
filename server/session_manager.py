import uuid

from server.session import GameSession, SessionStatus


class SessionManager:
    def __init__(self):
        self._sessions = {}

    def create_session(self, white_conn, black_conn):
        room_id = uuid.uuid4().hex[:8]
        session = GameSession(room_id, white_conn, black_conn)
        self._sessions[room_id] = session
        return session

    def get(self, room_id):
        return self._sessions.get(room_id)

    def remove(self, room_id):
        self._sessions.pop(room_id, None)

    def has_active_session(self, username):
        return any(
            session.status == SessionStatus.ACTIVE
            and username in {conn.username for conn in session.players.values()}
            for session in self._sessions.values()
        )

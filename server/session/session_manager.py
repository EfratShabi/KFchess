import uuid

from server.session.session import GameSession, SessionStatus


class SessionManager:
    def __init__(self):
        self._sessions = {}

    def create_session(self, white_conn, black_conn, room_id=None):
        if room_id is None:
            room_id = uuid.uuid4().hex[:8]
        session = GameSession(room_id, white_conn, black_conn)
        self._sessions[room_id] = session
        return session

    def get(self, room_id):
        return self._sessions.get(room_id)

    def restore(self, session):
        self._sessions[session.room_id] = session

    def remove(self, room_id):
        self._sessions.pop(room_id, None)

    def active_room_count(self):
        return len(self._sessions)

    def has_active_session(self, username):
        return any(
            session.status == SessionStatus.ACTIVE
            and username in {conn.username for conn in session.players.values()}
            for session in self._sessions.values()
        )

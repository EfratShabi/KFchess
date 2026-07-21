from dataclasses import dataclass


@dataclass
class WaitingPlayer:
    connection: object
    rating: int
    joined_at: float


class MatchmakingQueue:
    def __init__(self, rating_range=100, timeout_s=60):
        self._waiting = []
        self.rating_range = rating_range
        self.timeout_s = timeout_s

    def enqueue(self, connection, rating, now):
        self._waiting.append(WaitingPlayer(connection, rating, now))

    def try_match(self, connection, rating):
        for waiting in self._waiting:
            if abs(waiting.rating - rating) <= self.rating_range:
                self._waiting.remove(waiting)
                return waiting
        return None

    def expire(self, now):
        expired = [p for p in self._waiting if now - p.joined_at >= self.timeout_s]
        for p in expired:
            self._waiting.remove(p)
        return expired

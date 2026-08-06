import asyncio
from dataclasses import dataclass

from server.logging_config import get_logger


@dataclass
class GameResult:
    room_id: str
    white_username: str
    black_username: str
    winner: str
    white_rating_after: int
    black_rating_after: int


class ResultWriter:
    def __init__(self, repo):
        self.repo = repo
        self.queue = asyncio.Queue()

    def publish(self, result):
        self.queue.put_nowait(result)

    async def run(self):
        while True:
            result = await self.queue.get()
            try:
                self.repo.save_result(
                    result.room_id, result.white_username, result.black_username,
                    result.winner, result.white_rating_after, result.black_rating_after,
                )
                self.repo.update_rating(result.white_username, result.white_rating_after)
                self.repo.update_rating(result.black_username, result.black_rating_after)
            except Exception:
                get_logger().warning(f'failed to persist result for room {result.room_id}')
            finally:
                self.queue.task_done()

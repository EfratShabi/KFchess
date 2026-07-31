import asyncio

from core.config.constants import WHITE_COLOR
from server.db import AccountRepository
from server.result_writer import GameResult, ResultWriter


def test_publish_persists_result_row_and_updates_ratings(db_conn):
    repo = AccountRepository(db_conn)
    repo.register('alice', 'secret')
    repo.register('bob', 'secret')
    writer = ResultWriter(repo)

    async def scenario():
        task = asyncio.create_task(writer.run())
        writer.publish(GameResult(
            room_id='room1',
            white_username='alice',
            black_username='bob',
            winner=WHITE_COLOR,
            white_rating_after=1216,
            black_rating_after=1184,
        ))
        await writer.queue.join()
        task.cancel()

    asyncio.run(scenario())

    assert repo.get_rating('alice') == 1216
    assert repo.get_rating('bob') == 1184
    with db_conn.cursor() as cur:
        cur.execute(
            'SELECT room_id, white_username, black_username, winner FROM results WHERE room_id = %s',
            ('room1',),
        )
        row = cur.fetchone()
    assert row == ('room1', 'alice', 'bob', WHITE_COLOR)


def test_worker_keeps_running_after_a_failed_write():
    processed = []

    class FailingOnceRepo:
        def __init__(self):
            self.attempts = 0

        def save_result(self, room_id, *rest):
            self.attempts += 1
            if self.attempts == 1:
                raise RuntimeError('boom')
            processed.append(room_id)

        def update_rating(self, username, rating):
            pass

    writer = ResultWriter(FailingOnceRepo())

    async def scenario():
        task = asyncio.create_task(writer.run())
        writer.publish(GameResult('room1', 'alice', 'bob', WHITE_COLOR, 1216, 1184))
        writer.publish(GameResult('room2', 'alice', 'bob', WHITE_COLOR, 1216, 1184))
        await writer.queue.join()
        task.cancel()

    asyncio.run(scenario())

    assert processed == ['room2']

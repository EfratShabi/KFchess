import asyncio
import time

import websockets

from core.config.constants import WHITE_COLOR, BLACK_COLOR
from server import protocol
from server.db import init_db, AccountRepository
from server.login import authenticate
from server.logging_config import setup_logging, get_logger
from server.matchmaking import MatchmakingQueue
from server.protocol import MSG_TYPES
from server.session_manager import SessionManager

TICK_MS = 100
SNAPSHOT_EVERY_N_TICKS = 10
HOST = 'localhost'
PORT = 8765


async def join_queue(conn, matchmaking, sessions, mailboxes):
    match = matchmaking.try_match(conn, conn.rating)
    if match is not None:
        session = sessions.create_session(match.connection, conn)
        get_logger().info(f'match created: room={session.room_id}')
        await match.connection.send({'type': MSG_TYPES['MATCH_FOUND'], 'room_id': session.room_id,
                                      'color': WHITE_COLOR, 'opponent': conn.username})
        await conn.send({'type': MSG_TYPES['MATCH_FOUND'], 'room_id': session.room_id,
                          'color': BLACK_COLOR, 'opponent': match.connection.username})
        asyncio.create_task(run_session_tick_loop(session, sessions))
        waiting_mailbox = mailboxes.pop(match.connection, None)
        if waiting_mailbox is not None:
            await waiting_mailbox.put(session)
        return session

    mailbox = asyncio.Queue(maxsize=1)
    mailboxes[conn] = mailbox
    matchmaking.enqueue(conn, conn.rating, time.monotonic())
    try:
        return await asyncio.wait_for(mailbox.get(), timeout=matchmaking.timeout_s)
    except asyncio.TimeoutError:
        mailboxes.pop(conn, None)
        return None


async def handle_session_messages(session, conn):
    async for raw in conn.websocket:
        try:
            msg = protocol.decode(raw)
        except protocol.ProtocolError:
            continue
        if msg['type'] == MSG_TYPES['MOVE']:
            session.try_move(conn, tuple(msg['start']), tuple(msg['end']))
        elif msg['type'] == MSG_TYPES['JUMP']:
            session.try_jump(conn, msg['row'], msg['col'])


async def run_session_tick_loop(session, sessions):
    tick = 0
    while not session.service.is_game_over():
        await asyncio.sleep(TICK_MS / 1000)
        session.service.process_wait(TICK_MS)
        for msg in session.pull_outbox():
            await session.broadcast(msg)
        tick += 1
        if tick % SNAPSHOT_EVERY_N_TICKS == 0:
            await session.broadcast(session.snapshot())
    await session.broadcast(session.snapshot())
    sessions.remove(session.room_id)


async def expiry_loop(matchmaking):
    while True:
        await asyncio.sleep(1)
        matchmaking.expire(time.monotonic())


async def main():
    conn = init_db()
    repo = AccountRepository(conn)
    setup_logging()
    logger = get_logger()

    matchmaking = MatchmakingQueue()
    sessions = SessionManager()
    mailboxes = {}

    async def handler(websocket):
        logger.info('client connected')
        player = await authenticate(websocket, repo)
        if player is None:
            return
        session = await join_queue(player, matchmaking, sessions, mailboxes)
        if session is None:
            await player.send({'type': MSG_TYPES['NO_OPPONENT']})
            return
        await handle_session_messages(session, player)

    asyncio.create_task(expiry_loop(matchmaking))
    async with websockets.serve(handler, HOST, PORT):
        logger.info(f'server listening on ws://{HOST}:{PORT}')
        await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())

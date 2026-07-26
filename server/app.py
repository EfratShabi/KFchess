import asyncio
import time

import websockets

from core.config.constants import WHITE_COLOR, BLACK_COLOR
import protocol
from server.db import init_db, AccountRepository
from server.login import authenticate
from server.logging_config import setup_logging, get_logger
from server.game_result import apply_rating_changes
from server.matchmaking import MatchmakingQueue
from protocol import (
    FIELDS, MSG_TYPES, ErrorMessage, MatchFound, NoOpponent, OpponentDisconnected, list_to_position,
)
from server.session import SessionStatus
from server.session_manager import SessionManager

TICK_MS = 100
SNAPSHOT_EVERY_N_TICKS = 10
HOST = 'localhost'
PORT = 8765


async def join_queue(conn, matchmaking, sessions, mailboxes, repo):
    match = matchmaking.try_match(conn, conn.rating)
    if match is not None:
        session = sessions.create_session(match.connection, conn)
        get_logger().info(f'match created: room={session.room_id}')
        await match.connection.send(
            MatchFound(room_id=session.room_id, color=WHITE_COLOR, opponent=conn.username))
        await conn.send(
            MatchFound(room_id=session.room_id, color=BLACK_COLOR, opponent=match.connection.username))
        asyncio.create_task(run_session_tick_loop(session, sessions, repo))
        asyncio.create_task(broadcast_loop(session))
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
    try:
        async for raw in conn.websocket:
            try:
                msg = protocol.decode(raw)
            except protocol.ProtocolError:
                continue
            if msg[FIELDS['TYPE']] == MSG_TYPES['MOVE']:
                if not session.try_move(conn, list_to_position(msg[FIELDS['START']]), list_to_position(msg[FIELDS['END']])):
                    await conn.send(ErrorMessage(message='illegal move'))
            elif msg[FIELDS['TYPE']] == MSG_TYPES['JUMP']:
                if not session.try_jump(conn, msg[FIELDS['ROW']], msg[FIELDS['COL']]):
                    await conn.send(ErrorMessage(message='illegal jump'))
    finally:
        if session.status == SessionStatus.ACTIVE:
            session.end(SessionStatus.DISCONNECTED)
            await session.broadcast(OpponentDisconnected())


async def broadcast_loop(session):
    while True:
        msg = await session.next_broadcast()
        if msg is None:
            break
        await session.broadcast(msg)


async def run_session_tick_loop(session, sessions, repo):
    tick = 0
    while session.status == SessionStatus.ACTIVE and not session.service.is_game_over():
        await asyncio.sleep(TICK_MS / 1000)
        session.service.process_wait(TICK_MS)
        tick += 1
        if tick % SNAPSHOT_EVERY_N_TICKS == 0:
            await session.broadcast(session.snapshot())
    if session.status == SessionStatus.ACTIVE:
        session.end(SessionStatus.FINISHED)
        apply_rating_changes(session, repo)
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

    async def handle_player_lifecycle(websocket):
        logger.info('client connected')
        player = await authenticate(websocket, repo)
        if player is None:
            return
        if sessions.has_active_session(player.username):
            await player.send(ErrorMessage(message='you already have an active game'))
            return
        session = await join_queue(player, matchmaking, sessions, mailboxes, repo)
        if session is None:
            await player.send(NoOpponent())
            return
        await handle_session_messages(session, player)

    asyncio.create_task(expiry_loop(matchmaking))
    async with websockets.serve(handle_player_lifecycle, HOST, PORT):
        logger.info(f'server listening on ws://{HOST}:{PORT}')
        await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())

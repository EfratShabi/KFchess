import asyncio
import os
import time
import uuid

import websockets
from redis.asyncio import Redis

from core.config.constants import WHITE_COLOR, BLACK_COLOR
import protocol
from server.db import init_db, AccountRepository
from server.ws_auth import authenticate_with_token
from server.logging_config import setup_logging, get_logger
from server.game_result import compute_rating_changes
from server.matchmaking import MatchmakingQueue
from server.result_writer import GameResult, ResultWriter
from server.room_state import RoomState
from server.reconnect import try_reconnect
from server.recovery import recover_room
from server.tokens import create_ticket
from protocol import (
    FIELDS, MSG_TYPES, ErrorMessage, MatchFound, NoOpponent, OpponentReconnecting, list_to_position,
)
from server.session import SessionStatus
from server.session_manager import SessionManager

TICK_MS = 100
SNAPSHOT_EVERY_N_TICKS = 10
HOST = '0.0.0.0'
PORT = 8765


async def join_queue(conn, matchmaking, sessions, mailboxes, waiting_connections, result_writer, room_state, shard_id):
    matched_username = await matchmaking.try_match(conn.username, conn.rating)
    if matched_username is not None:
        opponent_conn = waiting_connections.pop(matched_username)
        session = sessions.create_session(opponent_conn, conn)
        epoch = await room_state.claim_room(session.room_id, shard_id)
        await room_state.save_players(session.room_id, opponent_conn.username, conn.username)
        ticket = create_ticket(session.room_id, epoch)
        get_logger().info(f'match created: room={session.room_id}')
        await opponent_conn.send(
            MatchFound(room_id=session.room_id, color=WHITE_COLOR, opponent=conn.username, ticket=ticket))
        await conn.send(
            MatchFound(room_id=session.room_id, color=BLACK_COLOR, opponent=opponent_conn.username, ticket=ticket))
        asyncio.create_task(run_session_tick_loop(session, sessions, result_writer, room_state))
        asyncio.create_task(broadcast_loop(session))
        waiting_mailbox = mailboxes.pop(matched_username, None)
        if waiting_mailbox is not None:
            await waiting_mailbox.put(session)
        return session

    mailbox = asyncio.Queue(maxsize=1)
    mailboxes[conn.username] = mailbox
    waiting_connections[conn.username] = conn
    await matchmaking.enqueue(conn.username, conn.rating, time.time())
    try:
        return await asyncio.wait_for(mailbox.get(), timeout=matchmaking.timeout_s)
    except asyncio.TimeoutError:
        mailboxes.pop(conn.username, None)
        waiting_connections.pop(conn.username, None)
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
            session.mark_disconnected(conn)
            await session.broadcast(OpponentReconnecting())


async def broadcast_loop(session):
    while True:
        msg = await session.next_broadcast()
        if msg is None:
            break
        await session.broadcast(msg)


async def run_session_tick_loop(session, sessions, result_writer, room_state):
    tick = 0
    while session.status == SessionStatus.ACTIVE and not session.service.is_game_over():
        await asyncio.sleep(TICK_MS / 1000)
        if session.is_paused():
            expired = session.expired_disconnects()
            if expired:
                if len(expired) == len(session.players):
                    session.end(SessionStatus.DISCONNECTED)
                else:
                    disconnected_color = expired[0]
                    winning_color = BLACK_COLOR if disconnected_color == WHITE_COLOR else WHITE_COLOR
                    session.service.force_game_over(winning_color)
            continue
        session.service.process_wait(TICK_MS)
        tick += 1
        if tick % SNAPSHOT_EVERY_N_TICKS == 0:
            snapshot = session.snapshot()
            await session.broadcast(snapshot)
            await room_state.save_snapshot(session.room_id, snapshot)
            await room_state.renew_lease(session.room_id)
    if session.status == SessionStatus.ACTIVE:
        session.end(SessionStatus.FINISHED)
        white_conn = session.players[WHITE_COLOR]
        black_conn = session.players[BLACK_COLOR]
        new_white, new_black = compute_rating_changes(session)
        result_writer.publish(GameResult(
            room_id=session.room_id,
            white_username=white_conn.username,
            black_username=black_conn.username,
            winner=session.service.get_winner(),
            white_rating_after=new_white,
            black_rating_after=new_black,
        ))
        await session.broadcast(session.snapshot())
    await room_state.clear_room(session.room_id)
    sessions.remove(session.room_id)


async def expiry_loop(matchmaking):
    while True:
        await asyncio.sleep(1)
        await matchmaking.expire(time.time())


async def main():
    conn = init_db()
    repo = AccountRepository(conn)
    setup_logging()
    logger = get_logger()

    redis_client = Redis(
        host=os.environ.get('REDIS_HOST', 'localhost'),
        port=int(os.environ.get('REDIS_PORT', 6379)),
        decode_responses=True,
    )
    matchmaking = MatchmakingQueue(redis_client)
    sessions = SessionManager()
    result_writer = ResultWriter(repo)
    room_state = RoomState(redis_client)
    shard_id = uuid.uuid4().hex[:8]
    mailboxes = {}
    waiting_connections = {}

    async def handle_player_lifecycle(websocket):
        logger.info('client connected')
        player = await authenticate_with_token(websocket, repo)
        if player is None:
            return
        if sessions.has_active_session(player.username):
            session = await try_reconnect(websocket, player, sessions)
            if session is None:
                return
            await handle_session_messages(session, player)
            return
        session = await join_queue(
            player, matchmaking, sessions, mailboxes, waiting_connections, result_writer, room_state, shard_id)
        if session is None:
            await player.send(NoOpponent())
            return
        await handle_session_messages(session, player)

    for orphaned_room_id in await room_state.find_orphaned_rooms():
        recovered_session = await recover_room(orphaned_room_id, room_state, repo, sessions, shard_id)
        if recovered_session is not None:
            logger.info(f'recovered room after a crash: room={orphaned_room_id}')
            asyncio.create_task(run_session_tick_loop(recovered_session, sessions, result_writer, room_state))
            asyncio.create_task(broadcast_loop(recovered_session))
        else:
            logger.info(f'could not recover orphaned room (missing data), cleared: room={orphaned_room_id}')

    asyncio.create_task(expiry_loop(matchmaking))
    asyncio.create_task(result_writer.run())
    async with websockets.serve(handle_player_lifecycle, HOST, PORT):
        logger.info(f'server listening on ws://{HOST}:{PORT}')
        await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())

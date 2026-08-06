import asyncio
import os
import time
import uuid

import websockets
from redis.asyncio import Redis

from core.config.constants import WHITE_COLOR, BLACK_COLOR
import protocol
from server.persistence.db import init_db, AccountRepository
from server.auth.ws_auth import authenticate_with_token
from server.logging_config import setup_logging, get_logger
from server.postgame.game_result import compute_rating_changes
from server.session.matchmaking import MatchmakingQueue
from server.persistence.result_writer import GameResult, ResultWriter
from server.session.room_state import RoomState
from server.session.allocator import GameAllocator, ShardInfo
from server.session.reconnect import try_reconnect
from server.session.recovery import recover_room
from server.auth.tokens import create_ticket
from protocol import (
    FIELDS, MSG_TYPES, ErrorMessage, MatchFound, NoOpponent, OpponentReconnecting, RoomCreated, list_to_position,
)
from server.session.session import SessionStatus
from server.session.session_manager import SessionManager

TICK_MS = 100
SNAPSHOT_EVERY_N_TICKS = 10
CLOSE_ROOM_TIMEOUT_S = 300
HOST = '0.0.0.0'
PORT = 8765


async def _start_session(white_conn, black_conn, sessions, result_writer, room_state, allocator, shard_id, room_id=None):
    session = sessions.create_session(white_conn, black_conn, room_id=room_id)
    candidates = [ShardInfo(shard_id=shard_id, active_rooms=sessions.active_room_count())]
    chosen_shard_id = allocator.choose_shard(candidates)
    epoch = await room_state.claim_room(session.room_id, chosen_shard_id)
    await room_state.save_players(session.room_id, white_conn.username, black_conn.username)
    ticket = create_ticket(session.room_id, epoch)
    get_logger().info(f'match created: room={session.room_id}')
    await white_conn.send(
        MatchFound(room_id=session.room_id, color=WHITE_COLOR, opponent=black_conn.username, ticket=ticket))
    await black_conn.send(
        MatchFound(room_id=session.room_id, color=BLACK_COLOR, opponent=white_conn.username, ticket=ticket))
    asyncio.create_task(run_session_tick_loop(session, sessions, result_writer, room_state))
    asyncio.create_task(broadcast_loop(session))
    return session


async def join_queue(conn, matchmaking, sessions, mailboxes, waiting_connections, result_writer, room_state, allocator, shard_id):
    matched_username = await matchmaking.try_match(conn.username, conn.rating)
    if matched_username is not None:
        opponent_conn = waiting_connections.pop(matched_username)
        session = await _start_session(opponent_conn, conn, sessions, result_writer, room_state, allocator, shard_id)
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


async def create_room(conn, pending_rooms):
    room_id = uuid.uuid4().hex[:8]
    mailbox = asyncio.Queue(maxsize=1)
    pending_rooms[room_id] = (conn, mailbox)
    await conn.send(RoomCreated(room_id=room_id))
    try:
        return await asyncio.wait_for(mailbox.get(), timeout=CLOSE_ROOM_TIMEOUT_S)
    except asyncio.TimeoutError:
        pending_rooms.pop(room_id, None)
        return None


async def join_room(conn, room_id, sessions, pending_rooms, result_writer, room_state, allocator, shard_id):
    pending = pending_rooms.pop(room_id, None)
    if pending is None:
        await conn.send(ErrorMessage(message='room not found'))
        return None
    creator_conn, mailbox = pending
    session = await _start_session(
        creator_conn, conn, sessions, result_writer, room_state, allocator, shard_id, room_id=room_id)
    await mailbox.put(session)
    return session


async def choose_mode(websocket):
    async for raw in websocket:
        try:
            msg = protocol.decode(raw)
        except protocol.ProtocolError:
            continue
        msg_type = msg[FIELDS['TYPE']]
        if msg_type in (MSG_TYPES['JOIN_ROOM'], MSG_TYPES['SPECTATE']):
            return msg_type, msg.get(FIELDS['ROOM_ID'])
        if msg_type in (MSG_TYPES['JOIN_QUEUE'], MSG_TYPES['CREATE_ROOM']):
            return msg_type, None
    return None, None


async def spectate_room(conn, room_id, sessions):
    session = sessions.get(room_id)
    if session is None or session.status != SessionStatus.ACTIVE:
        await conn.send(ErrorMessage(message='room not found or not active'))
        return None
    session.viewers.append(conn)
    await conn.send(session.snapshot())
    return session


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


async def handle_spectator_messages(session, conn):
    try:
        async for raw in conn.websocket:
            pass
    finally:
        session.viewers.remove(conn)


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
    allocator = GameAllocator()
    shard_id = uuid.uuid4().hex[:8]
    mailboxes = {}
    waiting_connections = {}
    pending_rooms = {}

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

        mode, room_id = await choose_mode(websocket)
        mode_handlers = {
            MSG_TYPES['JOIN_QUEUE']: (
                lambda: join_queue(player, matchmaking, sessions, mailboxes, waiting_connections,
                                    result_writer, room_state, allocator, shard_id),
                True,
                handle_session_messages,
            ),
            MSG_TYPES['CREATE_ROOM']: (
                lambda: create_room(player, pending_rooms),
                True,
                handle_session_messages,
            ),
            MSG_TYPES['JOIN_ROOM']: (
                lambda: join_room(player, room_id, sessions, pending_rooms, result_writer, room_state, allocator, shard_id),
                False,
                handle_session_messages,
            ),
            MSG_TYPES['SPECTATE']: (
                lambda: spectate_room(player, room_id, sessions),
                False,
                handle_spectator_messages,
            ),
        }
        entry = mode_handlers.get(mode)
        if entry is None:
            return
        handler, notify_no_opponent, message_handler = entry
        session = await handler()
        if session is None:
            if notify_no_opponent:
                await player.send(NoOpponent())
            return
        await message_handler(session, player)

    await asyncio.sleep(room_state.lease_ttl_seconds)
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

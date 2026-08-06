import queue
import threading
import time

import cv2
import httpx

import protocol
from protocol import (
    FIELDS, MSG_TYPES, ErrorMessage, MatchFound, NoOpponent, Ok, OpponentDisconnected, RoomCreated, Snapshot,
)
from interfaces.graphics.board_renderer import BoardRenderer
from interfaces.shared.client_state import ClientGameState
from interfaces.shared.graphics_constants import ESC_KEY
from interfaces.shared.network_client import NetworkClient
from interfaces.shared.networked_input import NetworkedInputController

API_URI = 'http://localhost:8000'
SERVER_URI = 'ws://localhost:8765'
RECONNECT_TIMEOUT_S = 60
ATTEMPT_TIMEOUT_S = 3


def _prompt_and_get_token():
    while True:
        username = input('username: ')
        password = input('password: ')
        choice = input('(l)ogin or (r)egister? ').strip().lower()
        endpoint = 'register' if choice == 'r' else 'login'
        response = httpx.post(
            f'{API_URI}/{endpoint}', json={FIELDS['USERNAME']: username, FIELDS['PASSWORD']: password})
        if response.status_code == 200:
            return response.json()['token']
        print(f"error: {response.json().get('detail', 'authentication failed')}")


QUICK_CHOICE = 'q'
CREATE_CHOICE = 'c'
JOIN_CHOICE = 'j'
SPECTATE_CHOICE = 's'

MODE_PROMPTS = {
    QUICK_CHOICE: lambda: protocol.encode(MSG_TYPES['JOIN_QUEUE']),
    CREATE_CHOICE: lambda: protocol.encode(MSG_TYPES['CREATE_ROOM']),
    JOIN_CHOICE: lambda: protocol.encode(
        MSG_TYPES['JOIN_ROOM'], **{FIELDS['ROOM_ID']: input('room code: ').strip()}),
    SPECTATE_CHOICE: lambda: protocol.encode(
        MSG_TYPES['SPECTATE'], **{FIELDS['ROOM_ID']: input('room code to watch: ').strip()}),
}


def _prompt_mode():
    choice = input(f'({QUICK_CHOICE})uick match, ({CREATE_CHOICE})reate room, '
                    f'({JOIN_CHOICE})oin room by code, or ({SPECTATE_CHOICE})pectate a room? ').strip().lower()
    build_message = MODE_PROMPTS.get(choice, MODE_PROMPTS[QUICK_CHOICE])
    return build_message()


def _authenticate_and_match(network_client, token):
    network_client.send(protocol.encode(MSG_TYPES['AUTHENTICATE'], token=token))
    while True:
        message = protocol.decode_message(network_client.incoming.get())
        if isinstance(message, Ok):
            network_client.send(_prompt_mode())
        elif isinstance(message, RoomCreated):
            print(f'room created! share this code with your friend: {message.room_id}')
        elif isinstance(message, ErrorMessage):
            print(f'error: {message.message}')
            return None
        elif isinstance(message, (MatchFound, Snapshot)):
            return message
        elif isinstance(message, NoOpponent):
            print('no opponent found within the timeout')
            return None


def _try_reconnect_once(token, ticket):
    network_client = NetworkClient(SERVER_URI)
    network_client.start()
    try:
        network_client.send(protocol.encode(MSG_TYPES['AUTHENTICATE'], token=token))
        auth_reply = protocol.decode_message(network_client.incoming.get(timeout=ATTEMPT_TIMEOUT_S))
        if not isinstance(auth_reply, Ok):
            return None

        network_client.send(protocol.encode(MSG_TYPES['RECONNECT'], ticket=ticket))
        reconnect_reply = protocol.decode_message(network_client.incoming.get(timeout=ATTEMPT_TIMEOUT_S))
        if not isinstance(reconnect_reply, Ok):
            return None
        return network_client
    except queue.Empty:
        return None


def _reconnect(token, ticket):
    deadline = time.monotonic() + RECONNECT_TIMEOUT_S
    while time.monotonic() < deadline:
        network_client = _try_reconnect_once(token, ticket)
        if network_client is not None:
            return network_client
        time.sleep(1)
    return None


def _start_reconnect(token, ticket, result_queue):
    result_queue.put(_reconnect(token, ticket))


def _drain_incoming(network_client, state):
    while True:
        try:
            raw = network_client.incoming.get_nowait()
        except queue.Empty:
            return
        message = protocol.decode_message(raw)
        if isinstance(message, Snapshot):
            state.apply_snapshot(message)
        elif isinstance(message, OpponentDisconnected):
            state.event_log.append('opponent disconnected')
        else:
            state.apply_event(message)


def main():
    token = _prompt_and_get_token()

    network_client = NetworkClient(SERVER_URI)
    network_client.start()

    result = _authenticate_and_match(network_client, token)
    if result is None:
        return

    state = ClientGameState()
    renderer = BoardRenderer()
    is_spectator = isinstance(result, Snapshot)

    if is_spectator:
        window_name = "KF Chess (spectating)"
        state.apply_snapshot(result)
    else:
        window_name = "KF Chess (multiplayer)"
        print(f'match found: room={result.room_id} color={result.color} opponent={result.opponent}')
        controller = NetworkedInputController(state, network_client, result.color)

    cv2.namedWindow(window_name)
    if not is_spectator:
        cv2.setMouseCallback(window_name, controller.mouse_callback)

    reconnect_thread = None
    reconnect_result = queue.Queue(maxsize=1)

    while True:
        if not is_spectator and network_client.disconnected.is_set() and not state.is_game_over():
            if reconnect_thread is None:
                print('connection lost, attempting to reconnect...')
                reconnect_thread = threading.Thread(
                    target=_start_reconnect, args=(token, result.ticket, reconnect_result), daemon=True)
                reconnect_thread.start()
            else:
                try:
                    new_client = reconnect_result.get_nowait()
                except queue.Empty:
                    pass
                else:
                    reconnect_thread = None
                    if new_client is None:
                        print('reconnect failed, giving up')
                        break
                    network_client = new_client
                    controller.network_client = network_client

        _drain_incoming(network_client, state)

        renderer.draw_board(state)
        renderer.draw_scores(state)
        renderer.draw_event_log(state)
        if state.is_game_over():
            renderer.draw_game_over_message()
        cv2.imshow(window_name, renderer.canvas.img)
        if cv2.waitKey(1) & 0xFF == ESC_KEY:
            break

    cv2.destroyWindow(window_name)


if __name__ == '__main__':
    main()

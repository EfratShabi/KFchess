import queue

import cv2

import protocol
from protocol import FIELDS, MSG_TYPES, ErrorMessage, MatchFound, NoOpponent, Ok, OpponentDisconnected, Snapshot
from interfaces.graphics.board_renderer import BoardRenderer
from interfaces.shared.client_state import ClientGameState
from interfaces.shared.graphics_constants import ESC_KEY
from interfaces.shared.network_client import NetworkClient
from interfaces.shared.networked_input import NetworkedInputController

SERVER_URI = 'ws://localhost:8765'


def _prompt_credentials():
    username = input('username: ')
    password = input('password: ')
    choice = input('(l)ogin or (r)egister? ').strip().lower()
    msg_type = MSG_TYPES['REGISTER'] if choice == 'r' else MSG_TYPES['LOGIN']
    return protocol.encode(msg_type, **{FIELDS['USERNAME']: username, FIELDS['PASSWORD']: password})


def _authenticate_and_match(network_client, first_message):
    network_client.send(first_message)
    logged_in = False
    while True:
        message = protocol.decode_message(network_client.incoming.get())
        if isinstance(message, Ok):
            logged_in = True
        elif isinstance(message, ErrorMessage):
            print(f'error: {message.message}')
            if not logged_in:
                network_client.send(_prompt_credentials())
            else:
                return None
        elif isinstance(message, MatchFound):
            return message
        elif isinstance(message, NoOpponent):
            print('no opponent found within the timeout')
            return None


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
    first_message = _prompt_credentials()

    network_client = NetworkClient(SERVER_URI)
    network_client.start()

    match = _authenticate_and_match(network_client, first_message)
    if match is None:
        return
    print(f'match found: room={match.room_id} color={match.color} opponent={match.opponent}')

    state = ClientGameState()
    controller = NetworkedInputController(state, network_client, match.color)
    renderer = BoardRenderer()

    window_name = "KF Chess (multiplayer)"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, controller.mouse_callback)

    while True:
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

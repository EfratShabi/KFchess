from core.domain.board import Board
from interfaces.cli.board_parser import parse_game_data, is_valid_input
from core.config.constants import COMMANDS
from core.real_time.real_time import RealTime
from core.services.game_service import GameService
from interfaces.shared.input_controller import InputController
import sys


def main():
    input_text = sys.stdin.read()
    lines = input_text.splitlines()
    chess, commands = parse_game_data(lines)

    if not is_valid_input(chess):
        return

    board = Board(chess)
    state = RealTime()
    service = GameService(board, state)
    controller = InputController(service)

    for line in commands:
        parts = line.split()
        if not parts:
            continue
        
        cmd_type = parts[0]
        if cmd_type == COMMANDS['CLICK']:
            x = int(parts[1])
            y = int(parts[2])
            controller.handle_click(x, y)

        elif cmd_type == COMMANDS['WAIT']:
            duration = int(parts[1])
            service.process_wait(duration)

        elif cmd_type == COMMANDS['PRINT']:
            print(service.get_board_string())

        elif cmd_type == COMMANDS['JUMP']:
            x = int(parts[1])
            y = int(parts[2])
            controller.handle_jump(x, y)

        if service.is_game_over():
            break

if __name__ == "__main__":
    main()
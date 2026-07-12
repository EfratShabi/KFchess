from domain.board import Board
from adapters.board_parser import parse_game_data, is_valid_input
from config.errors import ERR_ROW_WIDTH_MISMATCH
from services.real_time_arbiter import RealTimeArbiter
from services.game_service import GameService
import sys


def main():
    input_text = sys.stdin.read()
    lines = input_text.splitlines()
    chess, commands = parse_game_data(lines)

    if not is_valid_input(chess):
        return

    board = Board(chess)
    arbiter = RealTimeArbiter()
    service = GameService(board, arbiter)

    for line in commands:
        parts = line.split()
        if not parts:
            continue
        
        cmd_type = parts[0]
        if cmd_type == "click":
            x = int(parts[1])
            y = int(parts[2])
            service.process_click(x, y)

        elif cmd_type == "print":
            print(service.get_board_string())

        elif cmd_type == "wait":
            duration = int(parts[1])
            service.process_wait(duration)

        if service.is_game_over():
            break

if __name__ == "__main__":
    main()
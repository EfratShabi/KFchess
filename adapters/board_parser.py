import sys
from config import errors

def check_valid_token(chess):
    valid_char = {
        '.', 
        'wK', 'wQ', 'wR', 'wB', 'wN', 'wP', 
        'bK', 'bQ', 'bR', 'bB', 'bN', 'bP'  
    }
    for row in chess:
        for token in row:
            if token not in valid_char:
                print("ERROR", errors.ERR_UNKNOWN_TOKEN)
                return False               
    return True
    
def is_valid_input(chess):
    
    if not chess:
        return False

    length_cols = len(chess[0])
    for row in chess:
        if len(row) != length_cols:
            print("ERROR", errors.ERR_ROW_WIDTH_MISMATCH)
            return False

    return check_valid_token(chess)


def parse_game_data(lines):
    is_board = False
    is_command = False
    chess = []
    commands = []
    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue 
        if "Board:" in cleaned_line:
            is_board = True
            is_command = False
            continue
        elif "Commands:" in cleaned_line:
            is_command = True
            is_board = False
            continue

        if is_board:
            chess.append(cleaned_line.split()) 
        elif is_command:
            commands.append(cleaned_line)
            
    return chess, commands


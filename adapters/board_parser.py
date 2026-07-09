import sys

def check_valid(chess):
    valid_char = {
        '.', 
        'wK', 'wQ', 'wR', 'wB', 'wN', 'wP', 
        'bK', 'bQ', 'bR', 'bB', 'bN', 'bP'  
    }
    for row in chess:
        for token in row:
            if token not in valid_char:
                print("ERROR UNKNOWN_TOKEN")
                return 0
    return 1
    

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


def main():
    input_text = sys.stdin.read()   
    lines = input_text.splitlines()
    if not lines:
        return 

    chess, commands = parse_game_data(lines)
    if not chess:
        return

    first_row_tokens = chess[0]
    length_cols = len(first_row_tokens)
    length_rows = len(chess)
    
    for i in range(length_rows):
        current_row_tokens = chess[i] 
        if len(current_row_tokens) != length_cols:
            print("ERROR ROW_WIDTH_MISMATCH")
            return
    
    if check_valid(chess) == 0:
        return

if __name__ == "__main__":
    main()
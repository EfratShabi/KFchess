from piece import create_piece
from board_parser import parse_game_data, check_valid
from board import Board, MS_PER_CELL

import sys

def update_board_by_time(chess, current_time, pending_moves):
    moves_to_keep = []
    king_is_dead=False
    for move in pending_moves:
        if current_time >= move['arrival_time']:

            target = chess.get_piece_str(move['end'][0], move['end'][1])
            if target and target[1] == 'K': 
                king_is_dead=True

            chess.set_piece(move['end'][0], move['end'][1], move['piece'])
            chess.clear_cell(move['start'][0], move['start'][1])
            piece_str = move['piece']
            end_row = move['end'][0]
            #בדיקה אם החייל הגיע לסוף-נהפך למלכה
            if piece_str[1] == 'P':
                last_row = 0 if piece_str[0] == 'w' else len(chess.grid) - 1
                if end_row == last_row:
                    chess.set_piece(end_row, move['end'][1], piece_str[0] + 'Q')
        else:
            moves_to_keep.append(move)
            
    pending_moves.clear()
    pending_moves.extend(moves_to_keep)
    return king_is_dead

def print_board(chess, parts):
    if len(parts) > 1 and parts[1] == "board":
        for r in chess.grid:
            print(" ".join(r))

def handle_click(chess, row, col, selected_piece, current_time, pending_moves):
    if row < 0 or row >= chess.rows or col < 0 or col >= chess.cols:
        return selected_piece

    for move in pending_moves:
        if move['start'] == (row, col):
            return selected_piece
    #במידה וזה האיבר הראשון שהשחקן לחץ
    if selected_piece is None:
        if not chess.is_empty(row,col):
            selected_piece = (row, col)
        return selected_piece
    else:
        prev_row, prev_col = selected_piece
        selected_piece_name = chess.get_piece_str(prev_row, prev_col)

 #אם התבצע לחיצה על איבר מאותו הצבע -נתיחס ללחיצה האחרונה
        if not chess.is_empty(row, col) and chess.get_piece_color(row, col) == selected_piece_name[0]:
            selected_piece = (row, col)
            return selected_piece
        else:
            piece = create_piece(selected_piece_name)
            #אם לפי הדרישות הכלי יכול לזוז למקום החדש
            if piece.can_move(chess.grid, (prev_row, prev_col), (row, col)):     

                distance = max(abs(row - prev_row), abs(col - prev_col))
                duration = distance * MS_PER_CELL
                arrival_time = current_time + duration
                #נוסיף איבר חדש למערך האיברים שבתזוזה
                pending_moves.append({
                    'start': (prev_row, prev_col),
                    'end': (row, col),
                    'piece': selected_piece_name,
                    'arrival_time': arrival_time
                })
                #מנקים לפקודה חדשה של תזוזה
                selected_piece = None
            return selected_piece




def main():
    input_text = sys.stdin.read()   
    lines = input_text.splitlines()
    chess, commands = parse_game_data(lines)
    
    if not chess:
        return
        
    first_row_tokens = chess[0]
    length_cols = len(first_row_tokens)
    length_rows = len(chess)

    for i in range(length_rows):
        if len(chess[i]) != length_cols:
            print("ERROR ROW_WIDTH_MISMATCH")
            return

    if check_valid(chess) == 0:
        return
    chess = Board(chess) 

    selected_piece = None
    current_time = 0
    pending_moves = []
    game_over=False
    
    for line in commands:
        parts = line.split()
        if not parts:
            continue
        if not game_over:
            game_over=update_board_by_time(chess, current_time, pending_moves)
        cmd_type = parts[0]

        if cmd_type == "click" and game_over==False:
            x = int(parts[1])
            y = int(parts[2])
            col = x // 100
            row = y // 100
            selected_piece = handle_click(chess, row, col, selected_piece, current_time, pending_moves)
            

        elif cmd_type == "print":
            print_board(chess, parts)



        elif cmd_type == "wait":
            wait_duration = int(parts[1])
            current_time += wait_duration
    

if __name__ == "__main__":
    main()
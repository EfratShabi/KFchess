from domain.board import MS_PER_CELL

class RealTimeArbiter:
    def __init__(self):
        self.current_time = 0
        self.pending_moves = []
        self.game_over = False

    def advance_time(self, ms):
        self.current_time += ms

    def register_move(self, start, end, piece, distance):
        duration = distance * MS_PER_CELL
        arrival_time = self.current_time + duration
        self.pending_moves.append({
            'start': start,
            'end': end,
            'piece': piece,
            'arrival_time': arrival_time
        })
    

    def update_board_by_time(self, chess):
        if self.game_over:
            return
        moves_to_keep = []
        for move in self.pending_moves:
            if self.current_time >= move['arrival_time']:
                target = chess.get_piece_str(move['end'][0], move['end'][1])
                if target and target[1] == 'K':
                    self.game_over = True
                chess.set_piece(move['end'][0], move['end'][1], move['piece'])
                chess.clear_cell(move['start'][0], move['start'][1])
                piece_str = move['piece']
                end_row = move['end'][0]
                if piece_str[1] == 'P':
                    last_row = 0 if piece_str[0] == 'w' else len(chess.grid) - 1
                    if end_row == last_row:
                        chess.set_piece(end_row, move['end'][1], piece_str[0] + 'Q')
            else:
                moves_to_keep.append(move)
        self.pending_moves = moves_to_keep


    def is_moving(self, row, col):
        return any(move['start'] == (row, col) for move in self.pending_moves)
    


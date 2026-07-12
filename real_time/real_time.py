from config.constants import MS_PER_CELL,JUMP_DURATION_MS 
from domain.movement import Movement
from domain.jump import Jump

class RealTime:
    def __init__(self):
        self.current_time = 0
        self.pending_moves = []
        self.game_over = False

        self.movements = []  
        self.jumps = []     

    def is_moving(self, row, col):
        return any(m.start == (row, col) for m in self.movements)

    def is_jumping(self, row, col):
        return any(j.cell == (row, col) for j in self.jumps) 
    
    def advance_time(self, ms):
        self.current_time += ms

    def register_move(self, start, end, piece, distance):
        duration = distance * MS_PER_CELL
        arrival_time = self.current_time + duration
        self.movements.append(Movement(piece, start, end, arrival_time))

    def register_jump(self, cell, piece):
        arrival_time = self.current_time + JUMP_DURATION_MS
 
        self.jumps.append(Jump(piece, cell, arrival_time))
    

def update(self, board):
    if self.game_over:
        return
    due_movements = [m for m in self.movements if m.is_due(self.current_time)]  # אם תוסיפי גם ל-Movement
    for movement in due_movements:
        self._resolve_movement(movement, board)
        self.movements.remove(movement)
    due_jumps = [j for j in self.jumps if j.is_expired(self.current_time)]
    for jump in due_jumps:
        self.jumps.remove(jump)

def _resolve_movement(self, movement, board):
    landing_jump = next((j for j in self.jumps if j.intercepts(movement)), None)
    if landing_jump is not None:
        self._capture_midair(landing_jump, movement, board)
        return
    self._land_move(movement, board)



def _find_jump_at(self, cell):
    return next((j for j in self.jumps if j.cell == cell), None)


def _capture_midair(self, jump, movement, board):
    self.jumps.remove(jump)          # הכלי הקופץ נשאר במקומו - רק מסירים אותו מרשימת "באוויר"
    board.clear_cell(*movement.start)   # הכלי המגיע נעלם לגמרי

    if movement.piece[1] == KING:
        self.game_over = True


def _land_move(self, movement, board):
    target = board.get_piece_str(*movement.end)
    if target and target[1] == KING:
        self.game_over = True
    board.set_piece(*movement.end, movement.piece)
    board.clear_cell(*movement.start)



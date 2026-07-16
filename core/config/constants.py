# Player colors
WHITE_COLOR = 'w'
BLACK_COLOR = 'b'

# Command types
COMMANDS = {
    'CLICK': 'click',
    'WAIT': 'wait',
    'PRINT': 'print',
    'JUMP': 'jump'
}

# Jump mechanics states
IS_AIRBORNE = 'is_airborne'
JUMP_START_TIME = 'jump_start_time'
IS_MOVING = 'is_moving'


# Jump duration
JUMP_DURATION_MS = 1000
MS_PER_CELL = 1000

# Cooldown after landing (placeholder values, to be replaced by per-piece config data)
MOVE_COOLDOWN_MS = 2000  # "long_rest" after a move
JUMP_COOLDOWN_MS = 500   # "short_rest" after a jump

# Piece kinds
KING = 'K'
QUEEN = 'Q'
ROOK = 'R'
BISHOP = 'B'
KNIGHT = 'N'
PAWN = 'P'



EMPTY_CELL = '.'
MS_PER_CELL = 1000
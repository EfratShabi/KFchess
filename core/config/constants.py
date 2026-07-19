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

# Piece kinds
KING = 'K'
QUEEN = 'Q'
ROOK = 'R'
BISHOP = 'B'
KNIGHT = 'N'
PAWN = 'P'

# Points awarded for capturing each piece kind (king excluded - capturing it ends the game)
PIECE_VALUES = {
    QUEEN: 9,
    ROOK: 5,
    BISHOP: 3,
    KNIGHT: 3,
    PAWN: 1,
}

# Full piece names for display (avoids the BISHOP/BLACK 'B' collision in logs)
PIECE_NAMES = {
    KING: "King",
    QUEEN: "Queen",
    ROOK: "Rook",
    BISHOP: "Bishop",
    KNIGHT: "Knight",
    PAWN: "Pawn",
}



EMPTY_CELL = '.'
MS_PER_CELL = 1000
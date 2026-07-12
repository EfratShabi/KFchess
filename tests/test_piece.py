from domain.piece import Rook, Bishop, Pawn, Knight, King, Queen, create_piece
from domain.board import EMPTY_CELL

def test_rook_straight_move():
    """צריח יכול לנוע בקו ישר"""
    board = [
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL]
    ]
    rook = Rook('w')
    assert rook.can_move(board, (0, 0), (0, 2)) == True

def test_rook_blocked():
    """צריח לא יכול לנוע דרך כלי"""
    board = [
        [EMPTY_CELL, 'bP', EMPTY_CELL],
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL]
    ]
    rook = Rook('w')
    assert rook.can_move(board, (0, 0), (0, 2)) == False

def test_pawn_forward():
    """רגלי יכול לנוע צעד אחד קדימה"""
    board = [
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL]
    ]
    pawn = Pawn('w')
    assert pawn.can_move(board, (2, 1), (1, 1)) == True

def test_create_piece():
    """create_piece יוצר את הסוג הנכון"""
    piece = create_piece('wR')
    assert isinstance(piece, Rook)
    assert piece.color == 'w'
    assert str(piece) == 'wR'
def test_rook_blocked_by_friendly():
    """צריח חסום על ידי כלי ידידותי"""
    board = [
        [EMPTY_CELL, 'wP', EMPTY_CELL],
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
    ]
    rook = Rook('w')
    assert rook.can_move(board, (0, 0), (0, 2)) == False


def test_rook_blocked_by_enemy():
    """צריח חסום על ידי כלי אויב"""
    board = [
        [EMPTY_CELL, 'bP', EMPTY_CELL],
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
    ]
    rook = Rook('w')
    assert rook.can_move(board, (0, 0), (0, 2)) == False


def test_rook_diagonal_should_fail():
    """צריח לא יכול לנוע באלכסון"""
    board = [[EMPTY_CELL] * 3 for _ in range(3)]
    rook = Rook('w')
    assert rook.can_move(board, (0, 0), (2, 2)) == False


def test_rook_one_cell_move():
    """צריח יכול לנוע תא אחד"""
    board = [[EMPTY_CELL] * 2 for _ in range(2)]
    rook = Rook('w')
    assert rook.can_move(board, (0, 0), (0, 1)) == True
    assert rook.can_move(board, (0, 0), (1, 0)) == True


def test_rook_same_position():
    """צריח לא יכול להישאר באותו מקום"""
    board = [[EMPTY_CELL] * 2 for _ in range(2)]
    rook = Rook('w')
    assert rook.can_move(board, (0, 0), (0, 0)) == False


# ====== BISHOP - מקרי קצה ======

def test_bishop_straight_should_fail():
    """רץ לא יכול לנוע בקו ישר"""
    board = [[EMPTY_CELL] * 3 for _ in range(3)]
    bishop = Bishop('w')
    assert bishop.can_move(board, (0, 0), (0, 2)) == False
    assert bishop.can_move(board, (0, 0), (2, 0)) == False


def test_bishop_blocked_diagonal():
    """רץ חסום באלכסון"""
    board = [
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        [EMPTY_CELL, 'bP', EMPTY_CELL],
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
    ]
    bishop = Bishop('w')
    assert bishop.can_move(board, (0, 0), (2, 2)) == False


def test_bishop_not_perfect_diagonal():
    """רץ לא יכול לנוע למקום שאינו אלכסון מושלם"""
    board = [[EMPTY_CELL] * 4 for _ in range(4)]
    bishop = Bishop('w')
    assert bishop.can_move(board, (0, 0), (2, 3)) == False  # לא אותו מספר שורות ועמודות


def test_bishop_backwards_diagonal():
    """רץ יכול לנוע אחורה באלכסון"""
    board = [[EMPTY_CELL] * 3 for _ in range(3)]
    bishop = Bishop('w')
    assert bishop.can_move(board, (2, 2), (0, 0)) == True


# ====== KNIGHT - מקרי קצה ======

def test_knight_invalid_l_shapes():
    """פרש רק ב-L מדויק - לא תנועות אחרות"""
    board = [[EMPTY_CELL] * 4 for _ in range(4)]
    knight = Knight('w')
    
    # לא L - תנועות לא חוקיות
    assert knight.can_move(board, (1, 1), (1, 2)) == False  # ישר
    assert knight.can_move(board, (1, 1), (2, 2)) == False  # אלכסון
    assert knight.can_move(board, (1, 1), (3, 3)) == False  # אלכסון ארוך
    assert knight.can_move(board, (1, 1), (1, 1)) == False  # אותו מקום


def test_knight_all_valid_moves():
    """פרש יכול לנוע ל-8 כיוונים אפשריים"""
    board = [[EMPTY_CELL] * 5 for _ in range(5)]
    knight = Knight('w')
    center = (2, 2)
    
    # כל 8 התנועות החוקיות
    valid_moves = [
        (0, 1), (0, 3),  # למעלה
        (4, 1), (4, 3),  # למטה
        (1, 0), (3, 0),  # שמאלה
        (1, 4), (3, 4),  # ימינה
    ]
    
    for target in valid_moves:
        assert knight.can_move(board, center, target) == True


def test_knight_ignores_blocking():
    """פרש קופץ מעל כלים - לא נחסם"""
    board = [
        ['wP', 'wP', 'wP'],
        ['wP', EMPTY_CELL, 'wP'],
        ['wP', 'wP', 'wP'],
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
    ]
    knight = Knight('w')
    # פרש במרכז מוקף בכלים - עדיין יכול לקפוץ
    assert knight.can_move(board, (1, 1), (3, 2)) == True


# ====== KING - מקרי קצה ======

def test_king_two_steps_should_fail():
    """מלך לא יכול לנוע שני צעדים"""
    board = [[EMPTY_CELL] * 4 for _ in range(4)]
    king = King('w')
    assert king.can_move(board, (0, 0), (0, 2)) == False
    assert king.can_move(board, (0, 0), (2, 0)) == False
    assert king.can_move(board, (0, 0), (2, 2)) == False


def test_king_all_eight_directions():
    """מלך יכול לנוע לכל 8 הכיוונים - צעד אחד"""
    board = [[EMPTY_CELL] * 3 for _ in range(3)]
    king = King('w')
    center = (1, 1)
    
    # כל 8 הכיוונים
    directions = [
        (0, 0), (0, 1), (0, 2),
        (1, 0),         (1, 2),
        (2, 0), (2, 1), (2, 2),
    ]
    
    for target in directions:
        assert king.can_move(board, center, target) == True


def test_king_same_position():
    """מלך לא יכול להישאר באותו מקום"""
    board = [[EMPTY_CELL] * 2 for _ in range(2)]
    king = King('w')
    assert king.can_move(board, (0, 0), (0, 0)) == False


# ====== QUEEN - מקרי קצה ======

def test_queen_combines_rook_and_bishop():
    """מלכה = צריח + רץ"""
    board = [[EMPTY_CELL] * 4 for _ in range(4)]
    queen = Queen('w')
    
    # תנועות צריח
    assert queen.can_move(board, (0, 0), (0, 3)) == True  # אופקי
    assert queen.can_move(board, (0, 0), (3, 0)) == True  # אנכי
    
    # תנועות רץ
    assert queen.can_move(board, (0, 0), (3, 3)) == True  # אלכסון


def test_queen_blocked_like_rook():
    """מלכה חסומה כמו צריח"""
    board = [
        [EMPTY_CELL, 'bP', EMPTY_CELL],
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
    ]
    queen = Queen('w')
    assert queen.can_move(board, (0, 0), (0, 2)) == False


def test_queen_blocked_like_bishop():
    """מלכה חסומה כמו רץ"""
    board = [
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        [EMPTY_CELL, 'bP', EMPTY_CELL],
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
    ]
    queen = Queen('w')
    assert queen.can_move(board, (0, 0), (2, 2)) == False


def test_queen_invalid_move():
    """מלכה לא יכולה לנוע כמו פרש"""
    board = [[EMPTY_CELL] * 4 for _ in range(4)]
    queen = Queen('w')
    assert queen.can_move(board, (0, 0), (1, 2)) == False  # L-shape


# ====== PAWN - מקרי קצה ======

def test_pawn_white_backward_should_fail():
    """רגלי לבן לא יכול לנוע אחורה"""
    board = [[EMPTY_CELL] * 2 for _ in range(3)]
    pawn = Pawn('w')
    assert pawn.can_move(board, (1, 0), (2, 0)) == False  # למטה = אחורה עבור לבן


def test_pawn_black_backward_should_fail():
    """רגלי שחור לא יכול לנוע אחורה"""
    board = [[EMPTY_CELL] * 2 for _ in range(3)]
    pawn = Pawn('b')
    assert pawn.can_move(board, (1, 0), (0, 0)) == False  # למעלה = אחורה עבור שחור


def test_pawn_cannot_capture_forward():
    """רגלי לא יכול לאכול קדימה"""
    board = [
        [EMPTY_CELL],
        ['bP'],
        [EMPTY_CELL],
    ]
    pawn = Pawn('w')
    assert pawn.can_move(board, (2, 0), (1, 0)) == False  # יש כלי קדימה


def test_pawn_must_capture_diagonally():
    """רגלי חייב לאכול באלכסון"""
    board = [
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
    ]
    pawn = Pawn('w')
    # אלכסון ריק - לא יכול
    assert pawn.can_move(board, (2, 1), (1, 0)) == False
    assert pawn.can_move(board, (2, 1), (1, 2)) == False


def test_pawn_diagonal_with_enemy():
    """רגלי יכול לאכול אויב באלכסון"""
    board = [
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        ['bP', EMPTY_CELL, 'bP'],  # ← האויבים בשורה 1
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
    ]
    pawn = Pawn('w')
    assert pawn.can_move(board, (2, 1), (1, 0)) == True
    assert pawn.can_move(board, (2, 1), (1, 2)) == True


def test_pawn_two_steps_from_start():
    """רגלי יכול 2 צעדים רק מהשורה השנייה (לבן) או הראשונה (שחור)"""
    board = [[EMPTY_CELL] * 3 for _ in range(4)]
    
    # לבן משורה 2 (אינדקס 2 בלוח 4 שורות)
    pawn_w = Pawn('w')
    assert pawn_w.can_move(board, (2, 1), (0, 1)) == True
    
    # שחור משורה 1 (אינדקס 1)
    pawn_b = Pawn('b')
    assert pawn_b.can_move(board, (1, 1), (3, 1)) == True


def test_pawn_two_steps_blocked():
    """רגלי לא יכול 2 צעדים אם חסום באמצע"""
    board = [
        [EMPTY_CELL],
        ['bP'],       # חוסם
        [EMPTY_CELL],
        [EMPTY_CELL],
    ]
    pawn = Pawn('w')
    assert pawn.can_move(board, (2, 0), (0, 0)) == False


def test_pawn_sideways_should_fail():
    """רגלי לא יכול לנוע הצידה"""
    board = [[EMPTY_CELL] * 3 for _ in range(2)]
    pawn = Pawn('w')
    assert pawn.can_move(board, (1, 1), (1, 2)) == False


# ====== CREATE_PIECE - מקרי קצה ======

def test_create_piece_all_types():
    """create_piece יוצר את כל סוגי הכלים נכון"""
    pieces = {
        'wK': King, 'bK': King,
        'wQ': Queen, 'bQ': Queen,
        'wR': Rook, 'bR': Rook,
        'wB': Bishop, 'bB': Bishop,
        'wN': Knight, 'bN': Knight,
        'wP': Pawn, 'bP': Pawn,
    }
    
    for piece_str, expected_class in pieces.items():
        piece = create_piece(piece_str)
        assert isinstance(piece, expected_class)
        assert str(piece) == piece_str


# ====== לוחות קטנים - מקרי קצה ======


def test_pieces_on_2x2_board():
    """כלים על לוח 2x2 מינימלי"""
    board = [[EMPTY_CELL] * 2 for _ in range(2)]
    
    # צריח יכול
    assert Rook('w').can_move(board, (0, 0), (0, 1)) == True
    
    # רץ לא יכול - אין אלכסון באורך 2
    assert Bishop('w').can_move(board, (0, 0), (1, 1)) == True
    
    # פרש לא יכול - אין מקום ל-L
    assert Knight('w').can_move(board, (0, 0), (1, 1)) == False
    
    # מלך יכול
    assert King('w').can_move(board, (0, 0), (1, 1)) == True


# ====== טסטים לחסימות ======

def test_rook_blocked_horizontally():
    """צריח חסום אופקית"""
    board = [
        ['wR', 'wP', '.', '.', '.'],
    ]
    rook = Rook('w')
    
    # חסום על ידי חייל לבן
    assert rook.can_move(board, (0, 0), (0, 4)) == False
    
    # יכול לנוע עד החייל (לא כולל)
    assert rook.can_move(board, (0, 0), (0, 1)) == True


def test_rook_blocked_vertically():
    """צריך חסום אנכית"""
    board = [
        ['wR'],
        ['bP'],
        ['.'],
        ['.'],
    ]
    rook = Rook('w')
    
    # חסום על ידי חייל שחור
    assert rook.can_move(board, (0, 0), (3, 0)) == False
    
    # יכול לנוע עד החייל
    assert rook.can_move(board, (0, 0), (1, 0)) == True


def test_rook_multiple_blockers():
    """צריח עם כמה חוסמים"""
    board = [
        ['wR', '.', 'wP', '.', 'bP', '.'],
    ]
    rook = Rook('w')
    
    # החוסם הראשון קובע
    assert rook.can_move(board, (0, 0), (0, 3)) == False  # חסום ב-wP
    assert rook.can_move(board, (0, 0), (0, 5)) == False  # חסום לפני
    assert rook.can_move(board, (0, 0), (0, 2)) == True   # יכול להגיע


def test_bishop_blocked_diagonal():
    """רץ חסום באלכסון"""
    board = [
        ['wB', '.', '.', '.'],
        ['.', 'wP', '.', '.'],
        ['.', '.', '.', '.'],
        ['.', '.', '.', '.'],
    ]
    bishop = Bishop('w')
    
    # חסום על ידי חייל לבן
    assert bishop.can_move(board, (0, 0), (3, 3)) == False
    
    # יכול לנוע עד החייל
    assert bishop.can_move(board, (0, 0), (1, 1)) == True


def test_bishop_blocked_reverse_diagonal():
    """רץ חסום באלכסון הפוך"""
    board = [
        ['.', '.', '.', 'wB'],
        ['.', '.', 'bP', '.'],
        ['.', '.', '.', '.'],
        ['.', '.', '.', '.'],
    ]
    bishop = Bishop('w')
    
    # חסום על ידי חייל שחור
    assert bishop.can_move(board, (0, 3), (3, 0)) == False
    
    # יכול לנוע עד החייל
    assert bishop.can_move(board, (0, 3), (1, 2)) == True


def test_bishop_blocked_both_diagonals():
    """רץ חסום בשני כיוונים"""
    board = [
        ['.', '.', '.', '.', '.'],
        ['.', '.', '.', 'wP', '.'],  # רגלי לבן באלכסון למעלה-ימין
        ['.', '.', 'wB', '.', '.'],  # הרץ במרכז
        ['.', '.', '.', 'bP', '.'],  # רגלי שחור באלכסון למטה-ימין
        ['.', '.', '.', '.', '.'],
    ]
    bishop = Bishop('w')
    
    # חסום למעלה-ימין (כי יש wP ב-1,3 שמסתיר את 0,4)
    assert bishop.can_move(board, (2, 2), (0, 4)) == False
    
    # חסום למטה-ימין (כי יש bP ב-3,3 שמסתיר את 4,4)
    # שימי לב: הרץ יכול להכות את ה-bP ב-(3,3), אבל הוא לא יכול לעבור *דרך* החייל אל (4,4)
    assert bishop.can_move(board, (2, 2), (4, 4)) == False
    
    # יכול שמאלה למעלה - האלכסון הזה פנוי לחלוטין!
    assert bishop.can_move(board, (2, 2), (0, 0)) == True

def test_queen_blocked_like_rook():
    """מלכה חסומה כמו צריח"""
    board = [
        ['wQ', 'wP', '.', '.'],
    ]
    queen = Queen('w')
    
    # חסומה אופקית
    assert queen.can_move(board, (0, 0), (0, 3)) == False
    assert queen.can_move(board, (0, 0), (0, 1)) == True


def test_queen_blocked_like_bishop():
    """מלכה חסומה כמו רץ"""
    board = [
        ['wQ', '.', '.', '.'],
        ['.', 'bP', '.', '.'],
        ['.', '.', '.', '.'],
        ['.', '.', '.', '.'],
    ]
    queen = Queen('w')
    
    # חסומה באלכסון
    assert queen.can_move(board, (0, 0), (3, 3)) == False
    assert queen.can_move(board, (0, 0), (1, 1)) == True


def test_queen_one_direction_blocked_other_free():
    """מלכה חסומה בכיוון אחד, פנויה באחר"""
    board = [
        ['wQ', '.', '.', '.'],
        ['wP', '.', '.', '.'],
        ['.', '.', '.', '.'],
    ]
    queen = Queen('w')
    
    # חסומה למטה
    assert queen.can_move(board, (0, 0), (2, 0)) == False
    
    # פנויה ימינה
    assert queen.can_move(board, (0, 0), (0, 3)) == True


def test_pawn_blocked_two_step():
    """רגלי חסום בתנועה של שני צעדים"""
    board = [
        ['.'],
        ['bP'],  # חוסם
        ['.'],
        ['wP'],
    ]
    pawn = Pawn('w')
    
    # לא יכול 2 צעדים - יש חוסם
    assert pawn.can_move(board, (3, 0), (1, 0)) == False
    
    # יכול צעד אחד
    assert pawn.can_move(board, (3, 0), (2, 0)) == True


def test_rook_blocked_at_destination():
    """צריח - תא היעד תפוס"""
    board = [
        ['wR', '.', 'bP'],
    ]
    rook = Rook('w')
    
    # יכול לנוע לתא התפוס (אכילה)
    assert rook.can_move(board, (0, 0), (0, 2)) == True


def test_bishop_blocked_at_destination():
    """רץ - תא היעד תפוס"""
    board = [
        ['wB', '.', '.'],
        ['.', '.', '.'],
        ['.', '.', 'bP'],
    ]
    bishop = Bishop('w')
    
    # יכול לנוע לתא התפוס (אכילה)
    assert bishop.can_move(board, (0, 0), (2, 2)) == True


def test_rook_no_jump_over_friendly():
    """צריח לא יכול לקפוץ מעל כלי ידידותי"""
    board = [
        ['wR', '.', 'wP', '.', '.'],
    ]
    rook = Rook('w')
    
    # לא יכול לקפוץ מעל wP
    assert rook.can_move(board, (0, 0), (0, 4)) == False


def test_rook_no_jump_over_enemy():
    """צריח לא יכול לקפוץ מעל כלי אויב"""
    board = [
        ['wR', '.', 'bP', '.', '.'],
    ]
    rook = Rook('w')
    
    # לא יכול לקפוץ מעל bP
    assert rook.can_move(board, (0, 0), (0, 4)) == False


def test_bishop_no_jump_over_friendly():
    """רץ לא יכול לקפוץ מעל כלי ידידותי"""
    board = [
        ['wB', '.', '.', '.'],
        ['.', 'wP', '.', '.'],
        ['.', '.', '.', '.'],
        ['.', '.', '.', '.'],
    ]
    bishop = Bishop('w')
    
    # לא יכול לקפוץ מעל wP
    assert bishop.can_move(board, (0, 0), (3, 3)) == False


def test_bishop_no_jump_over_enemy():
    """רץ לא יכול לקפוץ מעל כלי אויב"""
    board = [
        ['wB', '.', '.', '.'],
        ['.', 'bP', '.', '.'],
        ['.', '.', '.', '.'],
        ['.', '.', '.', '.'],
    ]
    bishop = Bishop('w')
    
    # לא יכול לקפוץ מעל bP
    assert bishop.can_move(board, (0, 0), (3, 3)) == False


# ====== טסטים ספציפיים ל-has_blocker ======

def test_rook_clear_path_horizontal():
    """צריח - מסלול אופקי פנוי לגמרי"""
    board = [
        ['wR', '.', '.', '.', '.', '.'],
    ]
    rook = Rook('w')
    
    # כל המסלול פנוי
    assert rook.can_move(board, (0, 0), (0, 5)) == True
    assert rook.can_move(board, (0, 0), (0, 3)) == True
    assert rook.can_move(board, (0, 0), (0, 1)) == True


def test_rook_clear_path_vertical():
    """צריח - מסלול אנכי פנוי לגמרי"""
    board = [
        ['wR'],
        ['.'],
        ['.'],
        ['.'],
        ['.'],
    ]
    rook = Rook('w')
    
    # כל המסלול פנוי
    assert rook.can_move(board, (0, 0), (4, 0)) == True
    assert rook.can_move(board, (0, 0), (2, 0)) == True


def test_rook_blocker_at_different_positions():
    """צריח - חוסם במיקומים שונים במסלול"""
    board = [
        ['wR', '.', '.', '.', '.', '.'],
    ]
    rook = Rook('w')
    
    # חוסם במיקום 1
    board[0][1] = 'bP'
    assert rook.can_move(board, (0, 0), (0, 5)) == False
    assert rook.can_move(board, (0, 0), (0, 1)) == True  # יכול להגיע לחוסם
    board[0][1] = '.'
    
    # חוסם במיקום 3
    board[0][3] = 'wP'
    assert rook.can_move(board, (0, 0), (0, 5)) == False
    assert rook.can_move(board, (0, 0), (0, 2)) == True  # יכול להגיע לפני החוסם
    board[0][3] = '.'
    
    # חוסם במיקום 5 (תא היעד)
    board[0][5] = 'bK'
    assert rook.can_move(board, (0, 0), (0, 5)) == True  # יכול לאכול


def test_rook_backward_movement_with_blocker():
    """צריח - תנועה אחורה עם חוסם"""
    board = [
        ['.', '.', 'wP', '.', 'wR', '.'],
    ]
    rook = Rook('w')
    
    # תנועה אחורה (מימין לשמאל)
    assert rook.can_move(board, (0, 4), (0, 3)) == True   # צעד אחד אחורה
    assert rook.can_move(board, (0, 4), (0, 0)) == False  # חסום ב-wP


def test_bishop_clear_path_all_diagonals():
    """רץ - כל 4 האלכסונים ללא חסימה"""
    board = [
        ['.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.'],
        ['.', '.', 'wB', '.', '.'],
        ['.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.'],
    ]
    bishop = Bishop('w')
    
    # למעלה-שמאלה
    assert bishop.can_move(board, (2, 2), (0, 0)) == True
    
    # למעלה-ימינה
    assert bishop.can_move(board, (2, 2), (0, 4)) == True
    
    # למטה-שמאלה
    assert bishop.can_move(board, (2, 2), (4, 0)) == True
    
    # למטה-ימינה
    assert bishop.can_move(board, (2, 2), (4, 4)) == True


def test_bishop_blocker_near_start():
    """רץ - חוסם קרוב למקור"""
    board = [
        ['wB', '.', '.', '.'],
        ['.', 'bP', '.', '.'],
        ['.', '.', '.', '.'],
        ['.', '.', '.', '.'],
    ]
    bishop = Bishop('w')
    
    # חסום מיד אחרי צעד אחד
    assert bishop.can_move(board, (0, 0), (2, 2)) == False
    assert bishop.can_move(board, (0, 0), (3, 3)) == False
    assert bishop.can_move(board, (0, 0), (1, 1)) == True  # יכול להגיע לחוסם


def test_bishop_blocker_near_end():
    """רץ - חוסם קרוב ליעד"""
    board = [
        ['wB', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.'],
        ['.', '.', '.', 'wP', '.'],
        ['.', '.', '.', '.', '.'],
    ]
    bishop = Bishop('w')
    
    # חסום רק לפני היעד
    assert bishop.can_move(board, (0, 0), (4, 4)) == False
    assert bishop.can_move(board, (0, 0), (3, 3)) == False  # לא יכול גם לחוסם (ידידותי)
    assert bishop.can_move(board, (0, 0), (2, 2)) == True   # יכול לפני החוסם


def test_bishop_long_diagonal_with_blocker():
    """רץ - אלכסון ארוך עם חוסם באמצע"""
    board = [
        ['wB', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', 'bK', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.'],
    ]
    bishop = Bishop('w')
    
    # חסום באמצע מסלול ארוך
    assert bishop.can_move(board, (0, 0), (6, 6)) == False
    assert bishop.can_move(board, (0, 0), (3, 3)) == True  # יכול להגיע לחוסם


def test_queen_has_blocker_combines_both():
    """מלכה - has_blocker פועל גם לצריח וגם לרץ"""
    board = [
        ['wQ', '.', 'wP', '.', '.'],
        ['.', 'bP', '.', '.', '.'],
        ['.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.'],
    ]
    queen = Queen('w')
    
    # חסומה אופקית כמו צריח
    assert queen.can_move(board, (0, 0), (0, 4)) == False
    
    # חסומה באלכסון כמו רץ
    assert queen.can_move(board, (0, 0), (4, 4)) == False


def test_rook_empty_board_all_directions():
    """צריך בלוח ריק - יכול לנוע לכל הכיוונים"""
    board = [
        ['.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.'],
        ['.', '.', 'wR', '.', '.'],
        ['.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.'],
    ]
    rook = Rook('w')
    
    # למעלה
    assert rook.can_move(board, (2, 2), (0, 2)) == True
    # למטה
    assert rook.can_move(board, (2, 2), (4, 2)) == True
    # שמאלה
    assert rook.can_move(board, (2, 2), (2, 0)) == True
    # ימינה
    assert rook.can_move(board, (2, 2), (2, 4)) == True


def test_bishop_empty_board_all_diagonals():
    """רץ בלוח ריק - יכול לנוע לכל האלכסונים"""
    board = [
        ['.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.'],
        ['.', '.', 'wB', '.', '.'],
        ['.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.'],
    ]
    bishop = Bishop('w')
    
    # כל 4 הכיוונים פנויים
    assert bishop.can_move(board, (2, 2), (0, 0)) == True
    assert bishop.can_move(board, (2, 2), (0, 4)) == True
    assert bishop.can_move(board, (2, 2), (4, 0)) == True
    assert bishop.can_move(board, (2, 2), (4, 4)) == True


def test_rook_blocker_exactly_at_destination():
    """צריח - כלי אויב בדיוק ביעד (אכילה חוקית)"""
    board = [
        ['wR', '.', '.', 'bK'],
    ]
    rook = Rook('w')
    
    # יכול לאכול - היעד לא נחשב חוסם
    assert rook.can_move(board, (0, 0), (0, 3)) == True


def test_bishop_blocker_exactly_at_destination():
    """רץ - כלי אויב בדיוק ביעד (אכילה חוקית)"""
    board = [
        ['wB', '.', '.', '.'],
        ['.', '.', '.', '.'],
        ['.', '.', '.', '.'],
        ['.', '.', '.', 'bK'],
    ]
    bishop = Bishop('w')
    
    # יכול לאכול - היעד לא נחשב חוסם
    assert bishop.can_move(board, (0, 0), (3, 3)) == True


def test_bishop_two_blockers_in_diagonal():
    """רץ - שני חוסמים באלכסון"""
    board = [
        ['wB', '.', '.', '.', '.'],
        ['.', 'bP', '.', '.', '.'],
        ['.', '.', '.', '.', '.'],
        ['.', '.', '.', 'wP', '.'],
        ['.', '.', '.', '.', '.'],
    ]
    bishop = Bishop('w')
    
    # החוסם הראשון קובע
    assert bishop.can_move(board, (0, 0), (4, 4)) == False
    assert bishop.can_move(board, (0, 0), (2, 2)) == False
    assert bishop.can_move(board, (0, 0), (1, 1)) == True  # יכול לחוסם

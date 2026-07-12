from domain.board import Board
from real_time.real_time import RealTime
from services.game_service import GameService


def test_click_selects_piece():
    """לחיצה על כלי בוחרת אותו"""
    grid = [
        ['wR', '.', '.'],
        ['.', '.', '.'],
        ['.', '.', '.']
    ]
    board = Board(grid)
    arbiter = RealTimeArbiter()
    service = GameService(board, arbiter)

    service.process_click(50, 50)  # לוחץ על wR

    assert service.selected_piece == (0, 0)

def test_move_registers_in_arbiter():
    """תנועה נרשמת ב-arbiter"""
    grid = [
        ['wR', '.', '.'],
        ['.', '.', '.'],
        ['.', '.', '.']
    ]
    board = Board(grid)
    arbiter = RealTimeArbiter()
    service = GameService(board, arbiter)

    service.process_click(50, 50)   # בחירה
    service.process_click(250, 50)  # תנועה

    assert len(arbiter.pending_moves) == 1
    assert arbiter.pending_moves[0]['piece'] == 'wR'


# ====== מקרי קצה ל-GameService ======

def test_click_outside_board():
    """לחיצה מחוץ ללוח - לא אמור לקרוס"""
    grid = [
        ['wR', '.', '.'],
        ['.', '.', '.'],
        ['.', '.', '.']
    ]
    board = Board(grid)
    arbiter = RealTimeArbiter()
    service = GameService(board, arbiter)
    
    service.process_click(500, 500)  # מחוץ לגבולות
    
    assert service.selected_piece is None


def test_click_on_moving_piece():
    """לחיצה על כלי שכבר בתנועה - לא אמור לאפשר בחירה"""
    grid = [
        ['wR', '.', '.', '.'],
        ['.', '.', '.', '.'],
        ['.', '.', '.', '.'],
        ['.', '.', '.', '.']
    ]
    board = Board(grid)
    arbiter = RealTimeArbiter()
    service = GameService(board, arbiter)
    
    service.process_click(50, 50)   # בחירת wR
    service.process_click(350, 50)  # תנועה ל-column 3
    
    # wR עכשיו בתנועה - ננסה לבחור אותו שוב
    service.process_click(50, 50)   # לא אמור לאפשר
    
    assert service.selected_piece is None


def test_select_empty_cell():
    """לחיצה על תא ריק - לא אמור לבחור כלום"""
    grid = [
        ['.', '.', '.'],
        ['.', '.', '.'],
        ['.', '.', '.']
    ]
    board = Board(grid)
    arbiter = RealTimeArbiter()
    service = GameService(board, arbiter)
    
    service.process_click(150, 50)  # תא ריק
    
    assert service.selected_piece is None


def test_move_to_empty_and_occupied():
    """תנועה לתא ריק ולתא תפוס"""
    grid = [
        ['wR', '.', 'bK'],
        ['.', '.', '.'],
        ['.', '.', '.']
    ]
    board = Board(grid)
    arbiter = RealTimeArbiter()
    service = GameService(board, arbiter)
    
    # תנועה לתא ריק
    service.process_click(50, 50)   # בחירת wR
    service.process_click(150, 50)  # תנועה לתא ריק
    
    assert len(arbiter.pending_moves) == 1
    assert arbiter.pending_moves[0]['end'] == (0, 1)


def test_change_selection_same_color():
    """לחיצה על כלי אחר מאותו צבע - מחליף בחירה"""
    grid = [
        ['wR', 'wP', '.'],
        ['.', '.', '.'],
        ['.', '.', '.']
    ]
    board = Board(grid)
    arbiter = RealTimeArbiter()
    service = GameService(board, arbiter)
    
    service.process_click(50, 50)   # בחירת wR
    assert service.selected_piece == (0, 0)
    
    service.process_click(150, 50)  # לחיצה על wP
    assert service.selected_piece == (0, 1)  # החליף ל-wP


def test_invalid_move_keeps_selection():
    """מהלך לא חוקי - שומר את הבחירה"""
    grid = [
        ['wR', '.', '.', '.'],
        ['.', '.', '.', '.'],
        ['.', '.', '.', '.'],
        ['.', '.', '.', '.']
    ]
    board = Board(grid)
    arbiter = RealTimeArbiter()
    service = GameService(board, arbiter)
    
    service.process_click(50, 50)   # בחירת wR
    service.process_click(250, 150) # מהלך אלכסוני - לא חוקי לצריח
    
    # הבחירה צריכה להישאר
    assert service.selected_piece == (0, 0)
    assert len(arbiter.pending_moves) == 0


def test_game_over_blocks_clicks():
    """אחרי game over - clicks לא פועלים"""
    grid = [
        ['wR', '.', 'bK'],
        ['.', '.', '.'],
        ['.', '.', '.']
    ]
    board = Board(grid)
    arbiter = RealTimeArbiter()
    service = GameService(board, arbiter)
    
    # מבצע תנועה שאוכלת מלך
    service.process_click(50, 50)
    service.process_click(250, 50)
    
    # מקדם זמן כדי שהתנועה תסתיים
    service.process_wait(3000)
    
    assert service.is_game_over() == True
    
    # מנסה לבצע תנועה נוספת - לא אמור לעבוד
    service.process_click(250, 50)
    assert service.selected_piece is None


def test_multiple_pending_moves():
    """כמה תנועות בו זמנית"""
    grid = [
        ['wR', '.', '.'],
        ['bR', '.', '.']
    ]
    board = Board(grid)
    arbiter = RealTimeArbiter()
    service = GameService(board, arbiter)
    
    # תנועה של לבן
    service.process_click(50, 50)
    service.process_click(250, 50)
    
    # תנועה של שחור
    service.process_click(50, 150)
    service.process_click(250, 150)
    
    assert len(arbiter.pending_moves) == 2


def test_wait_advances_time():
    """wait מקדם זמן ומבצע תנועות"""
    grid = [['wR', '.', '.']]
    board = Board(grid)
    arbiter = RealTimeArbiter()
    service = GameService(board, arbiter)
    
    service.process_click(50, 50)
    service.process_click(250, 50)
    
    initial_time = arbiter.current_time
    service.process_wait(1000)
    
    assert arbiter.current_time == initial_time + 1000

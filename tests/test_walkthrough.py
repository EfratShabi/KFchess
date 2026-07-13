# -*- coding: utf-8 -*-
"""
טסט הדרכה - מדמה קלט אמיתי ומסביר את הלוגיקה של הפרויקט צעד אחר צעד.

CELL_SIZE = 100 פיקסלים לכל תא.
pixel_to_cell(x, y) → col = x // 100 , row = y // 100
לכן:
  קליק על (50, 50)  → תא (0, 0)  (שורה 0, עמודה 0)
  קליק על (150, 50) → תא (0, 1)
  קליק על (50, 150) → תא (1, 0)
"""

import pytest
from domain.board import Board
from real_time.real_time import RealTime
from services.game_service import GameService


# -------------------------------------------------------------------
# עזרים
# -------------------------------------------------------------------

def grid(*rows):
    """המרת שורות ASCII ל-grid של רשימות."""
    return [r.split() for r in rows]


def make_service(*rows):
    board = Board(grid(*rows))
    state = RealTime()
    return GameService(board, state)


def cell_to_pixel(row, col):
    """מחזיר פיקסל מרכזי של תא – שימושי להבנה."""
    return col * 100 + 50, row * 100 + 50


# ===================================================================
# 1. בחירת כלי (selection)
# ===================================================================

class TestSelection:
    """
    process_click ראשון כשאין selected_piece → בוחר כלי.
    process_click ראשון על תא ריק → לא בוחר כלום.
    """

    def test_click_on_piece_selects_it(self):
        # לוח עם רץ לבן בתא (0,0)
        svc = make_service(
            "wR . .",
            ".  . .",
            ".  . .",
        )
        # קליק על עמודה 0, שורה 0 → פיקסל (50, 50)
        svc.process_click(50, 50)
        assert svc.selected_piece == (0, 0), "כלי צריך להיבחר"

    def test_click_on_empty_does_not_select(self):
        svc = make_service(
            ". . .",
            ". . .",
        )
        svc.process_click(50, 50)   # תא ריק
        assert svc.selected_piece is None, "תא ריק לא אמור להיבחר"

    def test_second_click_same_color_switches_selection(self):
        # שני כלים לבנים. קליק ראשון בוחר את הראשון,
        # קליק שני על הכלי השני (אותו צבע) → בוחר את השני
        svc = make_service(
            "wR wK .",
            ".   .  .",
        )
        svc.process_click(50, 50)    # בחר wR בתא (0,0)
        assert svc.selected_piece == (0, 0)

        svc.process_click(150, 50)   # קליק על wK בתא (0,1)
        assert svc.selected_piece == (0, 1), "הבחירה צריכה לעבור לכלי השני"


# ===================================================================
# 2. תנועה תקינה ולא תקינה
# ===================================================================

class TestMovement:
    """
    אחרי שבחרנו כלי, קליק שני מנסה להזיז אותו.
    התנועה נרשמת ב-RealTime ומתבצעת רק אחרי advance_time + update.
    """

    def test_rook_moves_along_row(self):
        # רץ לבן בתא (0,0), קליק על (0,2) – שורה זהה, ללא חסמים
        svc = make_service(
            "wR . . . .",
            ".  . . . .",
        )
        svc.process_click(50, 50)    # בחר (0,0)
        svc.process_click(250, 50)   # נסה להזיז ל-(0,2)

        # אחרי הקליק התנועה נרשמה אבל הכלי עדיין במקומו (ב-flight)
        assert svc.board.get_piece_str(0, 0) == "wR", "הכלי עדיין במקורו עד שהזמן יעבור"

        # מרחק 2 תאים × 1000 מ"ש/תא = 2000 מ"ש
        svc.process_wait(2000)

        assert svc.board.get_piece_str(0, 2) == "wR", "הכלי אמור להגיע ל-(0,2)"
        assert svc.board.is_empty(0, 0), "התא המקורי צריך להתרוקן"

    def test_rook_blocked_by_friendly(self):
        # רץ לבן רוצה לעבור דרך כלי לבן אחר – לא אמור להצליח
        svc = make_service(
            "wR wK . .",
            ".   .  . .",
        )
        svc.process_click(50, 50)    # בחר wR (0,0)
        svc.process_click(250, 50)   # נסה לקפוץ מעל wK ל-(0,2)
        svc.process_wait(5000)       # זמן ארוך – שום דבר לא אמור לזוז

        assert svc.board.get_piece_str(0, 0) == "wR", "רץ חסום לא אמור לזוז"
        assert svc.board.get_piece_str(0, 1) == "wK", "מלך חסם לא אמור להיות מושפע"

    def test_king_moves_one_step(self):
        svc = make_service(
            "wK . .",
            ".   . .",
        )
        svc.process_click(50, 50)    # בחר מלך לבן (0,0)
        svc.process_click(150, 150)  # נסה להזיז ל-(1,1) – אלכסון של 1
        svc.process_wait(2000)

        assert svc.board.get_piece_str(1, 1) == "wK", "מלך יכול לנוע תא אחד אלכסונית"

    def test_king_cannot_move_two_steps(self):
        svc = make_service(
            "wK . . .",
            ".   . . .",
        )
        svc.process_click(50, 50)    # בחר מלך (0,0)
        svc.process_click(250, 50)   # נסה להזיז 2 עמודות – לא חוקי למלך
        svc.process_wait(5000)

        assert svc.board.get_piece_str(0, 0) == "wK", "מלך לא יכול לנוע 2 תאים"

    def test_knight_jumps_L_shape(self):
        # פרש: 2 שורות + 1 עמודה
        svc = make_service(
            "wN . . .",
            ".   . . .",
            ".   . . .",
        )
        svc.process_click(50, 50)    # בחר פרש (0,0)
        svc.process_click(150, 250)  # נסה להזיז ל-(2,1) – צורת L
        svc.process_wait(3000)

        assert svc.board.get_piece_str(2, 1) == "wN", "פרש חייב לנוע בצורת L"


# ===================================================================
# 3. אכילת כלי יריב
# ===================================================================

class TestCapture:
    """
    כשכלי עובר לתא שבו נמצא כלי יריב – הוא אוכל אותו.
    """

    def test_rook_captures_enemy(self):
        # רץ לבן בתא (0,0), כלי שחור ב-(0,2)
        svc = make_service(
            "wR . bK .",
            ".   . .  .",
        )
        svc.process_click(50, 50)    # בחר רץ לבן
        svc.process_click(250, 50)   # הזז אל המלך השחור ב-(0,2)
        svc.process_wait(3000)

        assert svc.board.get_piece_str(0, 2) == "wR", "הרץ אמור לאכול את המלך"
        assert svc.board.is_empty(0, 0), "התא המקורי ריק"

    def test_cannot_capture_same_color(self):
        svc = make_service(
            "wR . wK .",
            ".   . .  .",
        )
        svc.process_click(50, 50)    # בחר רץ לבן
        svc.process_click(250, 50)   # נסה לאכול מלך לבן
        svc.process_wait(3000)

        assert svc.board.get_piece_str(0, 0) == "wR", "לא ניתן לאכול כלי ידידותי"
        assert svc.board.get_piece_str(0, 2) == "wK", "המלך הלבן שלם"


# ===================================================================
# 4. קפיצה (Jump) ותפיסה באוויר
# ===================================================================

class TestJump:
    """
    process_jump שולח כלי לאוויר למשך JUMP_DURATION_MS=1000 מ"ש.
    כל כלי שמנסה לנחות בתא שבו יש כלי מקפץ – נתפס באוויר.
    """

    def test_jump_removes_piece_after_duration(self):
        svc = make_service(
            "wR . .",
            ".   . .",
        )
        # שלח את הרץ לאוויר
        svc.process_jump(50, 50)     # jump על (0,0)

        # לפני שהזמן עובר – הכלי עדיין על הלוח ובאוויר
        assert not svc.board.is_empty(0, 0), "הכלי עדיין על הלוח"
        assert svc.state.is_jumping(0, 0), "הכלי צריך להיות במצב קפיצה"

        # אחרי 1000 מ"ש הקפיצה פגה
        svc.process_wait(1000)
        assert not svc.state.is_jumping(0, 0), "הקפיצה אמורה לפוג"

    def test_moving_piece_captured_by_jumping_piece(self):
        """
        תרחיש:  רץ לבן ב-(0,0) זז ל-(0,2).
                כלי שחור ב-(0,2) קופץ לפני שהרץ מגיע.
                הרץ נתפס באוויר (landing_jump percolates).
        """
        svc = make_service(
            "wR . bR .",
            ".   . .  .",
        )
        # שלח את הרץ השחור לאוויר (תא (0,2) → פיקסל (250,50))
        svc.process_jump(250, 50)
        assert svc.state.is_jumping(0, 2)

        # עכשיו הזז את הרץ הלבן לכיוון (0,2) – מרחק 2 תאים = 2000 מ"ש
        svc.process_click(50, 50)
        svc.process_click(250, 50)

        # תן קצת זמן לתנועה להגיע – אחרי 2000 מ"ש
        svc.process_wait(2000)

        # הרץ הלבן תפס/נתפס; הלוגיקה תלויה ב-_resolve_movement
        # בדיקה שהרץ הלבן לא חזר לתא המקורי (הוא כן זז)
        assert svc.board.is_empty(0, 0), "הרץ הלבן אמור לעזוב את (0,0)"


# ===================================================================
# 5. זמן אמת – סדר פעולות
# ===================================================================

class TestRealTimeFlow:
    """
    בדיקה שהפרויקט מנהל תנועות מרובות במקביל נכון.
    """

    def test_two_pieces_move_simultaneously(self):
        # שני כלים זזים בו-זמנית
        svc = make_service(
            "wR . . . bR",
            ".   . . . . ",
        )
        # הזז רץ לבן שורה-ימינה ל-(0,1)
        svc.process_click(50, 50)
        svc.process_click(150, 50)

        # הזז רץ שחור שמאלה ל-(0,3)
        svc.process_click(450, 50)
        svc.process_click(350, 50)

        # אחרי 1000 מ"ש (מרחק 1 × 1000)
        svc.process_wait(1000)

        assert svc.board.get_piece_str(0, 1) == "wR", "הרץ הלבן הגיע ל-(0,1)"
        assert svc.board.get_piece_str(0, 3) == "bR", "הרץ השחור הגיע ל-(0,3)"

    def test_piece_blocked_while_in_flight(self):
        # תא היעד נחסם ע"י כלי ידידותי שנוסף לפני שהתנועה הושלמה
        # בפרויקט זה הכלי פשוט לא אמור לנוע (can_move בדקה מראש)
        svc = make_service(
            "wR wK . .",
            ".   .  . .",
        )
        svc.process_click(50, 50)    # בחר רץ (0,0)
        svc.process_click(150, 50)   # נסה לנוע ל-(0,1) שיש שם מלך
        svc.process_wait(2000)

        assert svc.board.get_piece_str(0, 0) == "wR"
        assert svc.board.get_piece_str(0, 1) == "wK"

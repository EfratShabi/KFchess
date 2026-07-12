# -*- coding: utf-8 -*-
"""
טסטים ל-Service/chess_game.py - מחלקת Chess.

בניגוד לשאר קבצי הטסטים (שבודקים יחידה אחת מבודדת), אלה טסטים
ברמת אינטגרציה: הם מפעילים את Chess כמו שה-Adapters/main.py עושה
(handle_click / handle_jump / advance_clock / print_game), ובודקים
את הפלט הסופי של הלוח. שימושי לוודא שכל היחידות (Board, Scheduler,
MoveRules, Pieces) עובדות נכון ביחד.

תרחישי ה"---" למטה (jump_lands_same_square וכו') הם בדיוק תרחישי
המרצה מ-cases.py, רק מורצים ישירות מול Chess במקום מול תהליך נפרד.
"""
import pytest
from services.chess_game import Chess
from adapters.board_mapper import CELL_SIZE
from config.constants import MS_PER_CELL as TIME_PER_CELL


def parse_board(*rows):
    """שורות ASCII כמו "wR . ." -> הפורמט שה-Chess מצפה לו (רשימת רשימות טוקנים)."""
    return [row.split() for row in rows]


def run_click(game, x, y):
    row, col = y // CELL_SIZE, x // CELL_SIZE
    game.handle_click(row, col)


def run_jump(game, x, y):
    row, col = y // CELL_SIZE, x // CELL_SIZE
    game.handle_jump(row, col)


def board_text(game):
    game.update_board()
    return "\n".join(
        " ".join(str(cell) for cell in row) for row in game.board.grid
    )


# ---------- אתחול ----------

def test_chess_accepts_a_well_formed_board():
    game = Chess(parse_board("wR . .", ". . ."))
    assert game.is_valid_setup is True


def test_chess_rejects_a_board_with_mismatched_row_widths(capsys):
    game = Chess([["wR", ".", "."], [".", "."]])
    assert game.is_valid_setup is False


# ---------- handle_click: בחירה ותנועה ----------

def test_click_on_empty_cell_selects_nothing():
    game = Chess(parse_board("wR . ."))
    run_click(game, x=150, y=50)  # (0,1) - ריק
    assert game.selected_piece_coords is None


def test_click_on_a_piece_then_a_legal_target_queues_a_move():
    game = Chess(parse_board("wR . ."))
    run_click(game, x=50, y=50)    # בוחר את wR ב-(0,0)
    run_click(game, x=250, y=50)   # יעד חוקי (0,2)
    assert len(game.scheduler.pending_moves) == 1
    assert game.selected_piece_coords is None  # הבחירה מתאפסת אחרי שליחת המהלך


def test_click_outside_the_board_deselects_the_current_piece():
    game = Chess(parse_board("wR . ."))
    run_click(game, x=50, y=50)     # בוחר כלי
    run_click(game, x=-100, y=-100)  # קליק מחוץ ללוח
    assert game.selected_piece_coords is None


def test_clicking_a_second_piece_of_the_same_color_reselects_it_instead_of_moving():
    game = Chess(parse_board("wR wN ."))
    run_click(game, x=50, y=50)   # בוחר wR
    run_click(game, x=150, y=50)  # קליק על wN - אותו צבע
    assert game.selected_piece_coords == (0, 1)
    assert game.scheduler.pending_moves == []


def test_clicking_an_illegal_target_deselects_without_queueing_a_move():
    game = Chess(parse_board(
        "wR . .",
        ". . .",
    ))
    run_click(game, x=50, y=50)   # בוחר wR ב-(0,0)
    run_click(game, x=250, y=150)  # יעד לא חוקי לצריח (1,2)
    assert game.selected_piece_coords is None
    assert game.scheduler.pending_moves == []


# ---------- handle_jump ----------

def test_handle_jump_queues_a_jump_action_for_an_occupied_cell():
    game = Chess(parse_board("wK . ."))
    run_jump(game, x=50, y=50)
    assert len(game.scheduler.active_jumps) == 1


def test_handle_jump_does_nothing_for_an_empty_cell():
    game = Chess(parse_board(". . ."))
    run_jump(game, x=50, y=50)
    assert game.scheduler.active_jumps == []


def test_handle_jump_does_nothing_when_a_move_is_already_pending_from_that_cell():
    game = Chess(parse_board("wR . ."))
    run_click(game, x=50, y=50)
    run_click(game, x=250, y=50)  # שולח את wR לתנועה
    run_jump(game, x=50, y=50)    # מנסה לקפוץ מהמשבצת שממנה הוא כבר יצא
    assert game.scheduler.active_jumps == []


# ---------- advance_clock / is_game_over ----------

def test_advance_clock_lands_a_pending_move_after_enough_time():
    game = Chess(parse_board("wR . ."))
    run_click(game, x=50, y=50)
    run_click(game, x=250, y=50)  # שתי משבצות -> 2 * TIME_PER_CELL
    game.advance_clock(2 * TIME_PER_CELL)
    assert board_text(game) == ". . wR"


def test_is_game_over_true_once_a_king_is_captured():
    game = Chess(parse_board("wR bK ."))
    run_click(game, x=50, y=50)
    run_click(game, x=150, y=50)
    game.advance_clock(TIME_PER_CELL)
    assert game.is_game_over is True


def test_advance_clock_does_nothing_once_the_game_is_over():
    game = Chess(parse_board("wR bK ."))
    run_click(game, x=50, y=50)
    run_click(game, x=150, y=50)
    game.advance_clock(TIME_PER_CELL)
    clock_after_win = game.scheduler.game_clock
    game.advance_clock(5000)
    assert game.scheduler.game_clock == clock_after_win


# ---------- תרחישי המרצה (מתוך cases.py), מורצים ישירות מול Chess ----------

INSTRUCTOR_SCENARIOS = [
    (
        "jump_lands_same_square",
        (". . .", ". wK .", ". . ."),
        [("jump", 150, 150), ("wait", 1000)],
        ". . .\n. wK .\n. . .",
    ),
    (
        "jump_catches_incoming_enemy",
        (". . .", "wK bR .", ". . ."),
        [("jump", 50, 150), ("click", 150, 150), ("click", 50, 150), ("wait", 1000)],
        ". . .\nwK . .\n. . .",
    ),
    (
        "late_jump_does_not_save_piece",
        (". . .", "wK bR .", ". . ."),
        [("click", 150, 150), ("click", 50, 150), ("wait", 1000), ("jump", 50, 150)],
        ". . .\nbR . .\n. . .",
    ),
    (
        "enemy_arrives_after_landing_and_captures_normally",
        (". . . .", "wK . . bR", ". . . ."),
        [("jump", 50, 150), ("wait", 1000), ("click", 350, 150), ("click", 50, 150), ("wait", 3000)],
        ". . . .\nbR . . .\n. . . .",
    ),
    (
        "cannot_jump_while_piece_is_moving",
        ("wR . .",),
        [("click", 50, 50), ("click", 250, 50), ("wait", 500), ("jump", 50, 50), ("wait", 1500)],
        ". . wR",
    ),
    (
        "airborne_piece_cannot_capture_same_color",
        (". . .", "wK wR .", ". . ."),
        [("jump", 50, 150), ("click", 150, 150), ("click", 50, 150), ("wait", 1000)],
        ". . .\nwK wR .\n. . .",
    ),
]


@pytest.mark.parametrize(
    "board_rows, commands, expected",
    [scenario[1:] for scenario in INSTRUCTOR_SCENARIOS],
    ids=[scenario[0] for scenario in INSTRUCTOR_SCENARIOS],
)
def test_instructor_scenario(board_rows, commands, expected):
    game = Chess(parse_board(*board_rows))
    assert game.is_valid_setup is True

    for cmd, *args in commands:
        if cmd == "click":
            run_click(game, *args)
        elif cmd == "jump":
            run_jump(game, *args)
        elif cmd == "wait":
            game.advance_clock(args[0])

    assert board_text(game) == expected
from config.constants import MS_PER_CELL


# ──────────────────────────────────────────────
# עזרים
# ──────────────────────────────────────────────

def parse_board(*rows):
    """שורות ASCII כמו "wR . ." -> רשימת רשימות טוקנים."""
    return [row.split() for row in rows]


def make_game(grid):
    """
    יוצר GameService מלוח נתון ומוסיף מאפיין is_valid_setup.
    משמש במקום Chess(grid) של הגרסה המקורית.
    """
    valid = is_valid_input(grid) if grid else False
    board = Board(grid)
    state = RealTime()
    service = GameService(board, state)
    service.is_valid_setup = valid
    return service


def run_click(game, x, y):
    """לחיצה בפיקסלים — process_click מטפל בהמרה לשורה/עמודה."""
    game.process_click(x, y)


def run_jump(game, x, y):
    """קפיצה בפיקסלים."""
    game.process_jump(x, y)


def board_text(game):
    """מחזיר את תוכן הלוח כמחרוזת לאחר עדכון אחרון."""
    game.state.update(game.board)
    return str(game.board)


# ──────────────────────────────────────────────
# אתחול
# ──────────────────────────────────────────────

def test_chess_accepts_a_well_formed_board():
    game = make_game(parse_board("wR . .", ". . ."))
    assert game.is_valid_setup is True


def test_chess_rejects_a_board_with_mismatched_row_widths(capsys):
    game = make_game([["wR", ".", "."], [".", "."]])
    assert game.is_valid_setup is False


# ──────────────────────────────────────────────
# process_click: בחירה ותנועה
# ──────────────────────────────────────────────

def test_click_on_empty_cell_selects_nothing():
    game = make_game(parse_board("wR . ."))
    run_click(game, x=150, y=50)  # (0,1) - ריק
    assert game.selected_piece is None


def test_click_on_a_piece_then_a_legal_target_queues_a_move():
    game = make_game(parse_board("wR . ."))
    run_click(game, x=50, y=50)    # בוחר את wR ב-(0,0)
    run_click(game, x=250, y=50)   # יעד חוקי (0,2)
    assert len(game.state.movements) == 1
    assert game.selected_piece is None  # הבחירה מתאפסת אחרי שליחת המהלך


def test_click_outside_the_board_deselects_the_current_piece():
    game = make_game(parse_board("wR . ."))
    run_click(game, x=50, y=50)      # בוחר כלי
    run_click(game, x=-100, y=-100)   # קליק מחוץ ללוח
    assert game.selected_piece is None


def test_clicking_a_second_piece_of_the_same_color_reselects_it_instead_of_moving():
    game = make_game(parse_board("wR wN ."))
    run_click(game, x=50, y=50)   # בוחר wR
    run_click(game, x=150, y=50)  # קליק על wN - אותו צבע
    assert game.selected_piece == (0, 1)
    assert game.state.movements == []


def test_clicking_an_illegal_target_deselects_without_queueing_a_move():
    game = make_game(parse_board("wR . .", ". . ."))
    run_click(game, x=50, y=50)    # בוחר wR ב-(0,0)
    run_click(game, x=250, y=150)  # יעד לא חוקי לצריח (1,2)
    assert game.selected_piece is None
    assert game.state.movements == []


# ──────────────────────────────────────────────
# process_jump
# ──────────────────────────────────────────────

def test_handle_jump_queues_a_jump_action_for_an_occupied_cell():
    game = make_game(parse_board("wK . ."))
    run_jump(game, x=50, y=50)
    assert len(game.state.jumps) == 1


def test_handle_jump_does_nothing_for_an_empty_cell():
    game = make_game(parse_board(". . ."))
    run_jump(game, x=50, y=50)
    assert game.state.jumps == []


def test_handle_jump_does_nothing_when_a_move_is_already_pending_from_that_cell():
    game = make_game(parse_board("wR . ."))
    run_click(game, x=50, y=50)
    run_click(game, x=250, y=50)   # שולח את wR לתנועה
    run_jump(game, x=50, y=50)     # מנסה לקפוץ מהמשבצת שממנה הוא כבר יצא
    assert game.state.jumps == []


# ──────────────────────────────────────────────
# process_wait / is_game_over
# ──────────────────────────────────────────────

def test_advance_clock_lands_a_pending_move_after_enough_time():
    game = make_game(parse_board("wR . ."))
    run_click(game, x=50, y=50)
    run_click(game, x=250, y=50)   # שתי משבצות -> 2 * MS_PER_CELL
    game.process_wait(2 * MS_PER_CELL)
    assert board_text(game) == ". . wR"


def test_is_game_over_true_once_a_king_is_captured():
    game = make_game(parse_board("wR bK ."))
    run_click(game, x=50, y=50)
    run_click(game, x=150, y=50)
    game.process_wait(MS_PER_CELL)
    assert game.is_game_over() is True


def test_advance_clock_does_nothing_once_the_game_is_over():
    game = make_game(parse_board("wR bK ."))
    run_click(game, x=50, y=50)
    run_click(game, x=150, y=50)
    game.process_wait(MS_PER_CELL)
    clock_after_win = game.state.current_time
    game.process_wait(5000)
    assert game.state.current_time == clock_after_win


# ──────────────────────────────────────────────
# תרחישי המרצה
# ──────────────────────────────────────────────

INSTRUCTOR_SCENARIOS = [
    (
        "jump_lands_same_square",
        (". . .", ". wK .", ". . ."),
        [("jump", 150, 150), ("wait", 1000)],
        ". . .\n. wK .\n. . .",
    ),
    (
        "jump_catches_incoming_enemy",
        (". . .", "wK bR .", ". . ."),
        [("jump", 50, 150), ("click", 150, 150), ("click", 50, 150), ("wait", 1000)],
        ". . .\nwK . .\n. . .",
    ),
    (
        "late_jump_does_not_save_piece",
        (". . .", "wK bR .", ". . ."),
        [("click", 150, 150), ("click", 50, 150), ("wait", 1000), ("jump", 50, 150)],
        ". . .\nbR . .\n. . .",
    ),
    (
        "enemy_arrives_after_landing_and_captures_normally",
        (". . . .", "wK . . bR", ". . . ."),
        [("jump", 50, 150), ("wait", 1000), ("click", 350, 150), ("click", 50, 150), ("wait", 3000)],
        ". . . .\nbR . . .\n. . . .",
    ),
    (
        "cannot_jump_while_piece_is_moving",
        ("wR . .",),
        [("click", 50, 50), ("click", 250, 50), ("wait", 500), ("jump", 50, 50), ("wait", 1500)],
        ". . wR",
    ),
    (
        "airborne_piece_cannot_capture_same_color",
        (". . .", "wK wR .", ". . ."),
        [("jump", 50, 150), ("click", 150, 150), ("click", 50, 150), ("wait", 1000)],
        ". . .\nwK wR .\n. . .",
    ),
]


@pytest.mark.parametrize(
    "board_rows, commands, expected",
    [scenario[1:] for scenario in INSTRUCTOR_SCENARIOS],
    ids=[scenario[0] for scenario in INSTRUCTOR_SCENARIOS],
)
def test_instructor_scenario(board_rows, commands, expected):
    game = make_game(parse_board(*board_rows))
    assert game.is_valid_setup is True

    for cmd, *args in commands:
        if cmd == "click":
            run_click(game, *args)
        elif cmd == "jump":
            run_jump(game, *args)
        elif cmd == "wait":
            game.process_wait(args[0])

    assert board_text(game) == expected



def parse_board(*rows):
    """שורות ASCII כמו "wR . ." -> הפורמט שה-Chess מצפה לו (רשימת רשימות טוקנים)."""
    return [row.split() for row in rows]


def run_click(game, x, y):
    row, col = y // CELL_SIZE, x // CELL_SIZE
    game.handle_click(row, col)


def run_jump(game, x, y):
    row, col = y // CELL_SIZE, x // CELL_SIZE
    game.handle_jump(row, col)


def board_text(game):
    game.update_board()
    return "\n".join(
        " ".join(str(cell) for cell in row) for row in game.board.grid
    )


# ---------- אתחול ----------

def test_chess_accepts_a_well_formed_board():
    game = Chess(parse_board("wR . .", ". . ."))
    assert game.is_valid_setup is True


def test_chess_rejects_a_board_with_mismatched_row_widths(capsys):
    game = Chess([["wR", ".", "."], [".", "."]])
    assert game.is_valid_setup is False


# ---------- handle_click: בחירה ותנועה ----------

def test_click_on_empty_cell_selects_nothing():
    game = Chess(parse_board("wR . ."))
    run_click(game, x=150, y=50)  # (0,1) - ריק
    assert game.selected_piece_coords is None


def test_click_on_a_piece_then_a_legal_target_queues_a_move():
    game = Chess(parse_board("wR . ."))
    run_click(game, x=50, y=50)    # בוחר את wR ב-(0,0)
    run_click(game, x=250, y=50)   # יעד חוקי (0,2)
    assert len(game.scheduler.pending_moves) == 1
    assert game.selected_piece_coords is None  # הבחירה מתאפסת אחרי שליחת המהלך


def test_click_outside_the_board_deselects_the_current_piece():
    game = Chess(parse_board("wR . ."))
    run_click(game, x=50, y=50)     # בוחר כלי
    run_click(game, x=-100, y=-100)  # קליק מחוץ ללוח
    assert game.selected_piece_coords is None


def test_clicking_a_second_piece_of_the_same_color_reselects_it_instead_of_moving():
    game = Chess(parse_board("wR wN ."))
    run_click(game, x=50, y=50)   # בוחר wR
    run_click(game, x=150, y=50)  # קליק על wN - אותו צבע
    assert game.selected_piece_coords == (0, 1)
    assert game.scheduler.pending_moves == []


def test_clicking_an_illegal_target_deselects_without_queueing_a_move():
    game = Chess(parse_board(
        "wR . .",
        ". . .",
    ))
    run_click(game, x=50, y=50)   # בוחר wR ב-(0,0)
    run_click(game, x=250, y=150)  # יעד לא חוקי לצריח (1,2)
    assert game.selected_piece_coords is None
    assert game.scheduler.pending_moves == []


# ---------- handle_jump ----------

def test_handle_jump_queues_a_jump_action_for_an_occupied_cell():
    game = Chess(parse_board("wK . ."))
    run_jump(game, x=50, y=50)
    assert len(game.scheduler.active_jumps) == 1


def test_handle_jump_does_nothing_for_an_empty_cell():
    game = Chess(parse_board(". . ."))
    run_jump(game, x=50, y=50)
    assert game.scheduler.active_jumps == []


def test_handle_jump_does_nothing_when_a_move_is_already_pending_from_that_cell():
    game = Chess(parse_board("wR . ."))
    run_click(game, x=50, y=50)
    run_click(game, x=250, y=50)  # שולח את wR לתנועה
    run_jump(game, x=50, y=50)    # מנסה לקפוץ מהמשבצת שממנה הוא כבר יצא
    assert game.scheduler.active_jumps == []


# ---------- advance_clock / is_game_over ----------

def test_advance_clock_lands_a_pending_move_after_enough_time():
    game = Chess(parse_board("wR . ."))
    run_click(game, x=50, y=50)
    run_click(game, x=250, y=50)  # שתי משבצות -> 2 * TIME_PER_CELL
    game.advance_clock(2 * MS_PER_CELL)
    assert board_text(game) == ". . wR"


def test_is_game_over_true_once_a_king_is_captured():
    game = Chess(parse_board("wR bK ."))
    run_click(game, x=50, y=50)
    run_click(game, x=150, y=50)
    game.advance_clock(MS_PER_CELL)
    assert game.is_game_over is True


def test_advance_clock_does_nothing_once_the_game_is_over():
    game = Chess(parse_board("wR bK ."))
    run_click(game, x=50, y=50)
    run_click(game, x=150, y=50)
    game.advance_clock(MS_PER_CELL)
    clock_after_win = game.scheduler.game_clock
    game.advance_clock(5000)
    assert game.scheduler.game_clock == clock_after_win


# ---------- תרחישי המרצה (מתוך cases.py), מורצים ישירות מול Chess ----------

INSTRUCTOR_SCENARIOS = [
    (
        "jump_lands_same_square",
        (". . .", ". wK .", ". . ."),
        [("jump", 150, 150), ("wait", 1000)],
        ". . .\n. wK .\n. . .",
    ),
    (
        "jump_catches_incoming_enemy",
        (". . .", "wK bR .", ". . ."),
        [("jump", 50, 150), ("click", 150, 150), ("click", 50, 150), ("wait", 1000)],
        ". . .\nwK . .\n. . .",
    ),
    (
        "late_jump_does_not_save_piece",
        (". . .", "wK bR .", ". . ."),
        [("click", 150, 150), ("click", 50, 150), ("wait", 1000), ("jump", 50, 150)],
        ". . .\nbR . .\n. . .",
    ),
    (
        "enemy_arrives_after_landing_and_captures_normally",
        (". . . .", "wK . . bR", ". . . ."),
        [("jump", 50, 150), ("wait", 1000), ("click", 350, 150), ("click", 50, 150), ("wait", 3000)],
        ". . . .\nbR . . .\n. . . .",
    ),
    (
        "cannot_jump_while_piece_is_moving",
        ("wR . .",),
        [("click", 50, 50), ("click", 250, 50), ("wait", 500), ("jump", 50, 50), ("wait", 1500)],
        ". . wR",
    ),
    (
        "airborne_piece_cannot_capture_same_color",
        (". . .", "wK wR .", ". . ."),
        [("jump", 50, 150), ("click", 150, 150), ("click", 50, 150), ("wait", 1000)],
        ". . .\nwK wR .\n. . .",
    ),
]


@pytest.mark.parametrize(
    "board_rows, commands, expected",
    [scenario[1:] for scenario in INSTRUCTOR_SCENARIOS],
    ids=[scenario[0] for scenario in INSTRUCTOR_SCENARIOS],
)
def test_instructor_scenario(board_rows, commands, expected):
    game = Chess(parse_board(*board_rows))
    assert game.is_valid_setup is True

    for cmd, *args in commands:
        if cmd == "click":
            run_click(game, *args)
        elif cmd == "jump":
            run_jump(game, *args)
        elif cmd == "wait":
            game.advance_clock(args[0])

    assert board_text(game) == expected

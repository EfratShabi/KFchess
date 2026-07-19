from core.config.constants import PIECE_NAMES


class GameLogger:
    def __init__(self):
        self.entries = []

    def on_event(self, event_type, **data):
        handler = getattr(self, f"_handle_{event_type}", None)
        if handler:
            handler(**data)

    @staticmethod
    def _color(piece_str):
        return piece_str[0].upper()

    @staticmethod
    def _name(piece_str):
        return PIECE_NAMES[piece_str[1]]

    def _handle_move_started(self, piece, start, end, time):
        self.entries.append(f"{self._color(piece)}: move {self._name(piece)} {start}->{end}")

    def _handle_move_landed(self, piece, end, time):
        self.entries.append(f"{self._color(piece)}: {self._name(piece)} arrived {end}")

    def _handle_move_captured(self, attacker, captured, position, time):
        self.entries.append(
            f"{self._color(attacker)}: {self._name(attacker)} captured "
            f"{self._color(captured)}'s {self._name(captured)} at {position}"
        )

    def _handle_jump_started(self, piece, cell, time):
        self.entries.append(f"{self._color(piece)}: jump {self._name(piece)} {cell}")

    def _handle_midair_capture(self, attacker, captured, position, time):
        self.entries.append(
            f"{self._color(attacker)}: {self._name(attacker)} captured "
            f"{self._color(captured)}'s {self._name(captured)} midair"
        )

    def _handle_game_over(self, winner, time):
        self.entries.append(f"Game Over -- {winner.upper()} wins")

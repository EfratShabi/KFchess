class Rest:
    def __init__(self, piece, position, ready_at):
        self.piece = piece
        self.position = position
        self.ready_at = ready_at

    def is_ongoing_cooldown(self, current_time):
        return current_time < self.ready_at

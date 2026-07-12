class Movement:
    def __init__(self, piece, start, end, arrival_time):
        self.piece = piece
        self.start = start
        self.end = end
        self.arrival_time = arrival_time  

    def is_due(self, current_time):
        return current_time >= self.arrival_time
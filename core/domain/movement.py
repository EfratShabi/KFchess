class Movement:
    def __init__(self, piece, start, end, start_time, arrival_time):
        self.piece = piece
        self.start = start
        self.end = end
        self.start_time = start_time
        self.arrival_time = arrival_time

    def is_due(self, current_time):
        return current_time >= self.arrival_time


    def progress(self, current_time):
        """מחזיר את התקדמות התנועה כיחס בין 0 (התחלה) ל-1 (הגעה), מוגבל לטווח הזה."""
        duration = self.arrival_time - self.start_time
        if duration <= 0:
            return 1.0
            
        ratio = (current_time - self.start_time) / duration
        return max(0.0, min(1.0, ratio))
class Jump:
    def __init__(self, piece, cell, arrival_time):
        self.piece = piece
        self.cell = cell
        self.arrival_time = arrival_time
    #פג התוקף
    def is_expired(self, current_time):
        return current_time > self.arrival_time
    
    #האם התנועה של האויב שנכנסת עכשיו לתא שלי, פגיעה ללכידה על ידי?
    def intercepts(self, movement):
        if movement.piece[0] == self.piece[0]:
            return False
        return movement.end == self.cell
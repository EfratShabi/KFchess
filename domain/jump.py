class Jump:
    def __init__(self, piece, cell, arrival_time):
        self.piece = piece
        self.cell = cell
        self.arrival_time = arrival_time
    
    def is_expired(self, current_time):
        """הקפיצה פוקעת אם הזמן עבר את arrival_time"""
        return current_time > self.arrival_time
    
    def intercepts(self, movement):
        """הקפיצה תופסת את התנועה אם:
        1. התנועה נוחתת בתא של הקפיצה
        2. התנועה היא של אויב (צבע שונה)
        """
        # התנועה חייבת להיות של אויב (צבע שונה)
        if movement.piece[0] == self.piece[0]:
            return False
        
        # התנועה חייבת להיחת בתא של הקפיצה
        return movement.end == self.cell
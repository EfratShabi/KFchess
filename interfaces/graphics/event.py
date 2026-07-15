# interfaces/graphics/ui_events.py
from interfaces.shared.pixel_math import pixel_to_cell 


class ClickEvent:
    def __init__(self, game_service, cell_size):
        self.game_service = game_service
        self.cell_size = cell_size

    def on_mouse_click(self, x, y):
        row, col = pixel_to_cell(x, y, self.cell_size)
        
        # 2. כאן המתרגם מעביר את הפקודה לליבה
        self.game_service.try_move((row, col)) 
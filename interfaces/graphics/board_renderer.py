from interfaces.graphics.img import Img

CELL_SIZE = 90          # כמה פיקסלים כל תא בלוח
BOARD_SIZE = 8           # 8x8 משבצות
BOARD_IMAGE_PATH = "assets/board.png"


def load_board_background():
    """טוענת את תמונת רקע הלוח, בגודל התואם למספר התאים * גודל תא."""
    pixel_size = CELL_SIZE * BOARD_SIZE
    return Img().read(BOARD_IMAGE_PATH, size=(pixel_size, pixel_size))


if __name__ == "__main__":
    canvas = load_board_background()
    canvas.show()
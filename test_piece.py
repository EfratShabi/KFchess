from piece import King, Queen, Rook, Bishop, Knight, Pawn, create_piece

board = [
    ['.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.'],
]

# Rook
rook = Rook('w')
assert rook.can_move(board, (0,0), (0,4)) == True,  "Rook straight"
board[0][2] = 'bP'
assert rook.can_move(board, (0,0), (0,4)) == False, "Rook blocked"
board[0][2] = '.'

# Bishop
bishop = Bishop('w')
assert bishop.can_move(board, (0,0), (3,3)) == True,  "Bishop diagonal"
assert bishop.can_move(board, (0,0), (0,4)) == False, "Bishop not straight"

# Pawn (white moves up = row decreases)
pawn_w = Pawn('w')
assert pawn_w.can_move(board, (3,0), (2,0)) == True,  "Pawn white forward"
assert pawn_w.can_move(board, (3,0), (4,0)) == False, "Pawn white wrong direction"

# Pawn capture
board[2][1] = 'bP'
assert pawn_w.can_move(board, (3,0), (2,1)) == True,  "Pawn white capture"
board[2][1] = '.'

# Knight
knight = Knight('w')
assert knight.can_move(board, (0,0), (2,1)) == True,  "Knight L-shape"
assert knight.can_move(board, (0,0), (1,1)) == False, "Knight not diagonal"

# King
king = King('w')
assert king.can_move(board, (2,2), (3,3)) == True,  "King one step"
assert king.can_move(board, (2,2), (4,4)) == False, "King two steps"

# Queen
queen = Queen('w')
assert queen.can_move(board, (0,0), (0,4)) == True,  "Queen straight"
assert queen.can_move(board, (0,0), (3,3)) == True,  "Queen diagonal"
assert queen.can_move(board, (0,0), (1,3)) == False, "Queen invalid"

# create_piece
p = create_piece('wR')
assert str(p) == 'wR' and type(p).__name__ == 'Rook', "create_piece wR"
p2 = create_piece('bK')
assert str(p2) == 'bK' and type(p2).__name__ == 'King', "create_piece bK"

print("All tests passed!")

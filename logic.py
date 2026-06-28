import random
from constants import ROWS, COLS

def new_board():
    b = [[0] * COLS for _ in range(ROWS)]
    spawn(b)
    spawn(b)
    return b

def spawn(board):
    empty = [(r, c) for r in range(ROWS) for c in range(COLS) if board[r][c] == 0]
    if empty:
        r, c = random.choice(empty)
        board[r][c] = 4 if random.random() < 0.1 else 2

def slide_left(row):
    tiles  = [v for v in row if v]
    result = []
    score  = 0
    skip   = False
    for i in range(len(tiles)):
        if skip:
            skip = False
            continue
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            merged = tiles[i] * 2
            result.append(merged)
            score += merged
            skip = True
        else:
            result.append(tiles[i])
    result += [0] * (COLS - len(result))
    return result, score

def rotate_cw(b):
    return [[b[ROWS - 1 - c][r] for c in range(COLS)] for r in range(ROWS)]

def push(board, direction):
    spins = {"left": 0, "right": 2, "up": 3, "down": 1}[direction]
    b = [row[:] for row in board]
    for _ in range(spins):
        b = rotate_cw(b)
    total = 0
    nb    = []
    for row in b:
        new_row, s = slide_left(row)
        nb.append(new_row)
        total += s
    for _ in range((4 - spins) % 4):
        nb = rotate_cw(nb)
    return nb, total, nb != board

def any_move(board):
    if any(board[r][c] == 0 for r in range(ROWS) for c in range(COLS)):
        return True
    for d in ("left", "right", "up", "down"):
        _, _, moved = push(board, d)
        if moved:
            return True
    return False

def has_2048(board):
    return any(board[r][c] == 2048 for r in range(ROWS) for c in range(COLS))

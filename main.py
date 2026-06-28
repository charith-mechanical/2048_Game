import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 800
ROWS, COLS    = 4, 4
CELL_W = WIDTH  // COLS
CELL_H = HEIGHT // ROWS
FPS    = 60
SPEED  = 18

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")

COL_BG      = (250, 248, 239)
COL_GRID    = (187, 173, 160)
COL_EMPTY   = (205, 193, 180)
COL_DARK    = (119, 110, 101)
COL_LIGHT   = (249, 246, 242)
COL_OVERLAY = (238, 228, 218)

TILE_COLORS = {
    2:    (237, 229, 218),
    4:    (238, 225, 201),
    8:    (243, 178, 122),
    16:   (246, 150, 101),
    32:   (247, 124,  95),
    64:   (247,  95,  59),
    128:  (237, 208, 115),
    256:  (237, 204,  99),
    512:  (236, 202,  80),
    1024: (235, 197,  60),
    2048: (234, 192,  40),
}

FONT_XL      = pygame.font.SysFont("comicsans", 58, bold=True)
FONT_LG      = pygame.font.SysFont("comicsans", 46, bold=True)
FONT_MD      = pygame.font.SysFont("comicsans", 36, bold=True)
FONT_SM      = pygame.font.SysFont("comicsans", 30, bold=True)
FONT_OVER_BIG = pygame.font.SysFont("comicsans", 64, bold=True)
FONT_OVER_SUB = pygame.font.SysFont("comicsans", 30)


def tile_color(v):
    return TILE_COLORS.get(v, (60, 58, 50))


def tile_font(v):
    if v < 100:   return FONT_XL
    if v < 1000:  return FONT_LG
    if v < 10000: return FONT_MD
    return FONT_SM


def tile_fg(v):
    return COL_DARK if v <= 4 else COL_LIGHT


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


def rotate_tracked_cw(b):
    return [[b[ROWS - 1 - c][r] for c in range(COLS)] for r in range(ROWS)]


def unrotate(r, c, spins):
    for _ in range((4 - spins) % 4):
        r, c = c, ROWS - 1 - r
    return r, c


def make_anims(old, direction):
    spins   = {"left": 0, "right": 2, "up": 3, "down": 1}[direction]
    tracked = [[(old[r][c], r, c) for c in range(COLS)] for r in range(ROWS)]
    for _ in range(spins):
        tracked = rotate_tracked_cw(tracked)

    tiles = []
    for dst_row in range(ROWS):
        items = [(v, sr, sc) for v, sr, sc in tracked[dst_row] if v]
        skip  = False
        dst_col = 0
        for i in range(len(items)):
            if skip:
                skip = False
                continue
            v, sr, sc = items[i]
            dr, dc = unrotate(dst_row, dst_col, spins)
            if i + 1 < len(items) and v == items[i + 1][0]:
                v2, sr2, sc2 = items[i + 1]
                tiles.append({"val": v * 2, "x": float(sc  * CELL_W), "y": float(sr  * CELL_H),
                               "tx": float(dc * CELL_W), "ty": float(dr * CELL_H), "done": False})
                tiles.append({"val": v,     "x": float(sc2 * CELL_W), "y": float(sr2 * CELL_H),
                               "tx": float(dc * CELL_W), "ty": float(dr * CELL_H), "done": False})
                skip = True
            else:
                tiles.append({"val": v, "x": float(sc * CELL_W), "y": float(sr * CELL_H),
                              "tx": float(dc * CELL_W), "ty": float(dr * CELL_H), "done": sc * CELL_W == dc * CELL_W and sr * CELL_H == dr * CELL_H})
            dst_col += 1
    return tiles


def step_anims(tiles):
    all_done = True
    for t in tiles:
        if t["done"]:
            continue
        dx = t["tx"] - t["x"]
        dy = t["ty"] - t["y"]
        dist = math.hypot(dx, dy)
        if dist <= SPEED:
            t["x"] = t["tx"]
            t["y"] = t["ty"]
            t["done"] = True
        else:
            t["x"] += SPEED * dx / dist
            t["y"] += SPEED * dy / dist
        all_done = False
    return all_done


def draw_cell(surf, v, px, py, w, h):
    pygame.draw.rect(surf, tile_color(v), (px, py, w, h), border_radius=4)
    label = tile_font(v).render(str(v), True, tile_fg(v))
    surf.blit(label, (px + w // 2 - label.get_width() // 2,
                      py + h // 2 - label.get_height() // 2))


def draw_grid(surf):
    gap = 8
    for r in range(ROWS):
        for c in range(COLS):
            px = c * CELL_W + gap
            py = r * CELL_H + gap
            pygame.draw.rect(surf, COL_EMPTY,
                             (px, py, CELL_W - gap * 2, CELL_H - gap * 2), border_radius=4)
    for row in range(1, ROWS):
        pygame.draw.line(surf, COL_GRID, (0, row * CELL_H), (WIDTH, row * CELL_H), 8)
    for col in range(1, COLS):
        pygame.draw.line(surf, COL_GRID, (col * CELL_W, 0), (col * CELL_W, HEIGHT), 8)
    pygame.draw.rect(surf, COL_GRID, (0, 0, WIDTH, HEIGHT), 8)


def draw_board(surf, board, flip=True):
    surf.fill(COL_BG)
    draw_grid(surf)
    for r in range(ROWS):
        for c in range(COLS):
            v = board[r][c]
            if v:
                draw_cell(surf, v, c * CELL_W, r * CELL_H, CELL_W, CELL_H)
    if flip:
        pygame.display.flip()


def draw_anim(surf, tiles):
    surf.fill(COL_BG)
    draw_grid(surf)
    for t in tiles:
        draw_cell(surf, t["val"], round(t["x"]), round(t["y"]), CELL_W, CELL_H)
    pygame.display.flip()


def make_overlay(line1, line2):
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    surf.fill((*COL_OVERLAY, 210))
    t1 = FONT_OVER_BIG.render(line1, True, COL_DARK)
    t2 = FONT_OVER_SUB.render(line2, True, COL_DARK)
    surf.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 2 - 60))
    surf.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2 + 20))
    return surf


def main():
    clock      = pygame.time.Clock()
    board      = new_board()
    score      = 0
    state      = "playing"
    anims      = []
    next_board = None

    overlay_won  = make_overlay("You reached 2048!", "R to play again    Q to quit")
    overlay_lost = make_overlay("Game over",         "R to play again    Q to quit")

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if state in ("won", "lost"):
                    if event.key == pygame.K_r:
                        board = new_board()
                        score = 0
                        state = "playing"
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        return

                elif state == "playing":
                    direction = {
                        pygame.K_LEFT:  "left",
                        pygame.K_RIGHT: "right",
                        pygame.K_UP:    "up",
                        pygame.K_DOWN:  "down",
                        pygame.K_a:     "left",
                        pygame.K_d:     "right",
                        pygame.K_w:     "up",
                        pygame.K_s:     "down",
                    }.get(event.key)

                    if direction:
                        nb, gained, moved = push(board, direction)
                        if moved:
                            score      += gained
                            anims       = make_anims(board, direction)
                            next_board  = nb
                            state       = "animating"

        if state == "animating":
            done = step_anims(anims)
            draw_anim(WINDOW, anims)
            if done:
                board = next_board
                spawn(board)
                if has_2048(board):
                    state = "won"
                elif not any_move(board):
                    state = "lost"
                else:
                    state = "playing"

        elif state == "playing":
            draw_board(WINDOW, board)

        elif state == "won":
            draw_board(WINDOW, board, flip=False)
            WINDOW.blit(overlay_won, (0, 0))
            pygame.display.flip()

        elif state == "lost":
            draw_board(WINDOW, board, flip=False)
            WINDOW.blit(overlay_lost, (0, 0))
            pygame.display.flip()


if __name__ == "__main__":
    main()
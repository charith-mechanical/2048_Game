import pygame
import math
from constants import *

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

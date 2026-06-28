import pygame

pygame.init()

WIDTH, HEIGHT = 800, 800
ROWS, COLS    = 4, 4
CELL_W = WIDTH  // COLS
CELL_H = HEIGHT // ROWS
FPS    = 60
SPEED  = 18

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

FONT_XL       = pygame.font.SysFont("comicsans", 58, bold=True)
FONT_LG       = pygame.font.SysFont("comicsans", 46, bold=True)
FONT_MD       = pygame.font.SysFont("comicsans", 36, bold=True)
FONT_SM       = pygame.font.SysFont("comicsans", 30, bold=True)
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

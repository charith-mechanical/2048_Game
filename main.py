import pygame
from engine.constants import FPS, WINDOW
from engine.logic import new_board, push, spawn, has_2048, any_move
from engine.ui import make_overlay, make_anims, step_anims, draw_anim, draw_board

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
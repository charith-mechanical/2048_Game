# 2048: Python & Pygame Implementation

Welcome to the **2048 Python Game**! This repository is a fully functional, animated, and rigorously refactored version of the classic 2048 puzzle game built using Python and the Pygame library.

## Project Structure & Architecture

The original code was built as a single monolithic script. To ensure enterprise-grade maintainability, separation of concerns, and mathematical purity, the codebase has been aggressively refactored into four deeply decoupled modules:

### 1. `constants.py` (The Configuration Layer)
This file acts as the Single Source of Truth (SSOT) for all global configurations. 
* **Grid Topologies:** Defines the mathematical dimensions of the grid (`ROWS`, `COLS`, `WIDTH`, `HEIGHT`).
* **Color Palettes:** Contains the exact hex/RGB color mappings for every possible tile up to $2048$ (e.g., the bright golden hue of the 2048 tile).
* **Typography:** Pre-initializes all Pygame `SysFont` objects to prevent costly re-initialization during the rendering loop.

### 2. `logic.py` (The Mathematical Engine)
This module is entirely UI-agnostic. It contains the pure mathematical matrix operations required to simulate the 2048 mechanics.
* **Random Spawning (`spawn`):** Uses a pseudo-random number generator to place a $2$ (90% probability) or a $4$ (10% probability) in an empty coordinate.
* **Matrix Rotation (`rotate_cw`):** Implements a linear algebra transposition and reversal to rotate the $4 \times 4$ matrix $90^\circ$ clockwise.
* **State Verification (`has_2048`, `any_move`):** Evaluates whether the user has reached the win condition, or if the system has reached a terminal state (loss condition).

### 3. `ui.py` (The Rendering & Animation Engine)
This handles the rasterization and visual feedback of the state machine.
* **Linear Interpolation (`step_anims`):** Calculates Euclidean distances ($d = \sqrt{\Delta x^2 + \Delta y^2}$) between the origin coordinates and target coordinates, stepping the tiles forward by a specific `SPEED` vector to create smooth sliding animations.
* **Rasterization (`draw_board`, `draw_grid`):** Paints the Pygame surface objects using the constants provided by the configuration layer.

### 4. `main.py` (The State Machine Controller)
This is the entry point of the program. It orchestrates the entire application using an Infinite Loop pattern that polls for hardware interrupts (keyboard events).

## Deep Dive: Game Mechanics & Matrix Mathematics

### The Matrix Grid
The board is mathematically represented as a two-dimensional array (a $4 \times 4$ matrix). Empty spaces are represented by the scalar `0`. 

```python
board = [
    [0, 2, 0, 4],
    [2, 0, 8, 8],
    [0, 0, 0, 0],
    [4, 4, 4, 4]
]
```

### The Algorithm: Rotation-Based Sliding
Writing custom algorithmic logic to handle collisions for all four cardinal directions (Up, Down, Left, Right) requires massive code duplication and is highly prone to index out-of-bounds errors. Instead, this codebase uses an elegant **matrix rotational mapping algorithm**. 

The core sliding logic (`slide_left`) is *only* written for the "Left" direction. 
When the user presses an arrow key, the board is rotated clockwise by a specific number of $90^\circ$ turns to mechanically map the user's intended direction to "Left".

* **Left:** Rotate 0 times.
* **Up:** Rotate 3 times ($270^\circ$).
* **Right:** Rotate 2 times ($180^\circ$).
* **Down:** Rotate 1 time ($90^\circ$).

#### Example: Sliding Left
Let's analyze what happens when the matrix row is `[4, 4, 8, 0]` and the user slides left.
1. `slide_left` condenses the non-zero elements to the left: `[4, 4, 8]`.
2. It iterates through the array checking for identical adjacent elements.
3. It finds `4` and `4`, merging them into `8`.
4. It appends the untouched `8`. The array is now `[8, 8]`.
5. Finally, it pads the remaining length of the matrix row with `0`s, resulting in `[8, 8, 0, 0]`.

After the slide operation completes across all rows, the entire matrix is counter-rotated back to its original physical orientation to prepare for rendering.

## Deep Dive: The Game State Machine

The game operates on a Finite State Machine (FSM) architecture. The `main.py` loop constantly tracks the variable `state`, which can hold one of four string values:

1. **`playing`**: The default state. The engine waits for `pygame.event.get()` keyboard events. If a valid move occurs, it triggers the `make_anims` function and transitions to the `animating` state.
2. **`animating`**: The engine blocks new keyboard inputs and executes `step_anims` every frame. Once the Euclidean distance between all moving tiles and their targets reaches zero, it evaluates the board. If `2048` is present, it goes to `won`. If no moves are left, it goes to `lost`. Otherwise, it returns to `playing`.
3. **`won`**: A transparent surface is blitted over the screen. The system only listens for the `R` key (to reset) or `Q` (to quit).
4. **`lost`**: Identical to `won`, but displays the Game Over overlay.

## Unique Implementations & Engine Optimizations

What makes this implementation stand out compared to a standard 2048 clone? We have injected several architectural and performance optimizations:

### 1. Font Object Caching (Zero-Allocation Rendering)
In a naive Pygame implementation, calling `pygame.font.SysFont("comicsans", 30)` inside the rendering loop creates severe memory leaks and drops the framerate because it instantiates a new Font object 60 times a second.
**Our Optimization:** All fonts (`FONT_XL`, `FONT_SM`, etc.) are pre-compiled in `constants.py` exactly once when the program launches. During the `draw_cell` loop, we simply reference the pointer to the pre-rendered font in memory, resulting in $O(1)$ lookup times and zero garbage collection overhead during frames.

### 2. State-Decoupled Animation Engine
Most grid games update the internal state *after* the animation finishes, which creates massive lag in input buffering.
**Our Optimization:** The moment a user presses an arrow key, the `board` matrix is instantly fully evaluated and mathematically solved in `logic.py` under 1 millisecond. The old board and the *mathematically guaranteed* new board are then passed to `make_anims()`, which simply interpolates the visual sprites. The game knows you won or lost *before* the animation even finishes rendering.

### 3. $O(N)$ Matrix Rotation
By using the algorithm `[[b[ROWS - 1 - c][r] for c in range(COLS)] for r in range(ROWS)]`, we achieve in-place (technically newly allocated but minimal overhead) matrix transposition. Instead of writing 4 distinct collision loops (Left, Right, Up, Down) which scales to roughly 120 lines of redundant, hard-to-maintain code, our rotational abstraction reduces the entire physics engine to just 30 lines.

### 4. Non-Uniform Probability Spawning
When a board shifts, a new tile must spawn in one of the empty `0` coordinates. 
In `logic.py`, the `spawn(board)` function uses a strict non-uniform distribution:
```python
board[r][c] = 4 if random.random() < 0.1 else 2
```
This precisely matches the mathematical constraints of the original 2048 game: a 90% chance to spawn a $2$, and a 10% chance to spawn a $4$. This prevents the grid from scaling too quickly while still introducing necessary RNG to keep the entropy high.

## Requirements
* Python 3.x
* [Pygame](https://www.pygame.org/)

You can install the required dependencies by running:
```bash
pip install pygame
```

## How to Run
Simply execute the main script from your terminal:
```bash
python main.py
```

## Controls
* `W` / `Up Arrow` : Slide Up
* `A` / `Left Arrow` : Slide Left
* `S` / `Down Arrow` : Slide Down
* `D` / `Right Arrow` : Slide Right
* `R` : Restart the game (available after winning or losing)
* `Q` / `Esc` : Quit the application

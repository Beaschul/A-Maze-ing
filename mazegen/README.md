# mazegen

Reusable maze generator, built for the 42 A-Maze-ing project.

- **Perfect mazes**: exactly one path between any two cells (recursive
  backtracker).
- **Pac-Man boards** (`perfect=False`): connected, with loops and few
  dead-ends.
- A fully closed **"42"** pattern drawn in the middle when the maze is big
  enough (9x7 or more).
- **Shortest path** from entry to exit (BFS), as cells and as `N/E/S/W`.
- **Reproducible**: same seed, same maze.

Pure standard library, Python 3.10+, fully typed (`py.typed`). The package
never prints, reads input or exits: every problem raises `MazeError`.

## Install

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

## Usage

```python
from mazegen import Direction, MazeError, MazeGenerator

maze = MazeGenerator(20, 15, entry=(0, 0), exit=(19, 14),
                     perfect=True, seed=42)
maze.generate()

maze.seed                              # 42 (drawn at random if not given)
maze.grid                              # grid[y][x]: 4-bit wall mask per cell
maze.has_wall((0, 0), Direction.NORTH)  # True
maze.solution                          # [(0, 0), (1, 0), ...] entry -> exit
maze.solution_directions               # "EESEN..."
maze.pattern_cells                     # cells of the "42" (always closed)

try:
    MazeGenerator(20, 15, entry=(0, 0), exit=(20, 0))
except MazeError as err:
    print(err)  # exit (20, 0) is outside the 20x15 maze
```

### Conventions

- Coordinates are `(x, y)`: `x` = column, `y` = row; grids are indexed
  `grid[y][x]`.
- Wall bits: `NORTH = 1`, `EAST = 2`, `SOUTH = 4`, `WEST = 8`; a set bit
  means the wall is closed.
- `WIDTH` / `HEIGHT` go from `MIN_DIMENSION` (2) to `MAX_DIMENSION` (500).
- One instance = one maze. For a new maze, create a new `MazeGenerator`.

### Animation data

`generate()` also records `maze.carve_history` (the walls opened, in order)
and `maze.search_history` (the cells visited by the BFS, in order), so an
application can replay the construction and the search.

### Writing the output file

```python
from mazegen.writer import write_output

write_output(
    "maze.txt",
    hex_rows=["".join(f"{c:x}" for c in row) for row in maze.grid],
    entry=(0, 0),
    exit=(19, 14),
    path_moves=maze.solution_directions,
)
```

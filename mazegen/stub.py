"""TEMPORARY stub of MazeGenerator, with a fixed 5x5 maze.

It lets the application (render, menu, output file, animation) be built
before the real algorithms exist. Delete this file once ``generate`` is
implemented (#6, #7).

Usage in the app, instead of ``MazeGenerator(...)``::

    from mazegen.stub import StubMazeGenerator
    maze = StubMazeGenerator()
    maze.generate()

The maze, entry at the top-left and exit at the bottom-right::

    +--+--+--+--+--+
    |En|           |
    +  +  +--+  +  +
    |  |  |     |  |
    +  +  +  +--+--+
    |     |        |
    +--+--+--+--+  +
    |     |     |  |
    +  +--+--+  +  +
    |            Ex|
    +--+--+--+--+--+
"""

from mazegen.directions import Direction
from mazegen.errors import MazeError
from mazegen.maze_generator import MazeGenerator
from mazegen.walls import Cell

_N, _E, _S, _W = (Direction.NORTH, Direction.EAST,
                  Direction.SOUTH, Direction.WEST)

STUB_GRID: tuple[str, ...] = (
    "B9513",
    "AA96E",
    "C6C53",
    "97D3A",
    "C5546",
)
"""Wall masks, one hexadecimal digit per cell (same as the output file)."""

STUB_CARVE_HISTORY: tuple[tuple[Cell, Direction], ...] = (
    ((0, 0), _S), ((0, 1), _S), ((0, 2), _E), ((1, 2), _N),
    ((1, 1), _N), ((1, 0), _E), ((2, 0), _E), ((3, 0), _E),
    ((4, 0), _S), ((3, 0), _S), ((3, 1), _W), ((2, 1), _S),
    ((2, 2), _E), ((3, 2), _E), ((4, 2), _S), ((4, 3), _S),
    ((4, 4), _W), ((3, 4), _N), ((3, 3), _W), ((3, 4), _W),
    ((2, 4), _W), ((1, 4), _W), ((0, 4), _N), ((0, 3), _E),
)

STUB_SEARCH_HISTORY: tuple[Cell, ...] = (
    (0, 0), (0, 1), (0, 2), (1, 2), (1, 1), (1, 0), (2, 0), (3, 0),
    (4, 0), (3, 1), (4, 1), (2, 1), (2, 2), (3, 2), (4, 2), (4, 3),
    (4, 4),
)

STUB_SOLUTION: tuple[Cell, ...] = (
    (0, 0), (0, 1), (0, 2), (1, 2), (1, 1), (1, 0), (2, 0), (3, 0),
    (3, 1), (2, 1), (2, 2), (3, 2), (4, 2), (4, 3), (4, 4),
)


class StubMazeGenerator(MazeGenerator):
    """MazeGenerator that always returns the same 5x5 perfect maze.

    The maze is too small for the "42", so :attr:`pattern_cells` is empty
    (the app should print its "too small" error message).
    """

    def __init__(self, seed: int | None = 42) -> None:
        """Create the 5x5 maze, entry (0, 0) and exit (4, 4)."""
        super().__init__(5, 5, (0, 0), (4, 4), perfect=True, seed=seed)
        self._generated = False

    def generate(self) -> None:
        """Mark the fixed maze as generated."""
        self._generated = True

    def has_wall(self, cell: Cell, direction: Direction) -> bool:
        """Tell whether the wall ``direction`` of ``cell`` is closed."""
        x, y = cell
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise MazeError(f"cell {cell} is outside the maze")
        return bool(self.grid[y][x] & direction)

    @property
    def grid(self) -> list[list[int]]:
        """Copy of the wall masks, indexed ``grid[y][x]``."""
        self._require_generated()
        return [[int(digit, 16) for digit in row] for row in STUB_GRID]

    @property
    def pattern_cells(self) -> set[Cell]:
        """Always empty: 5x5 is too small for the "42"."""
        self._require_generated()
        return set()

    @property
    def solution(self) -> list[Cell]:
        """Cells of the shortest path, from entry to exit."""
        self._require_generated()
        return list(STUB_SOLUTION)

    @property
    def solution_directions(self) -> str:
        """The shortest path written with N, E, S and W."""
        self._require_generated()
        return "SSENNEESWSEESS"

    @property
    def carve_history(self) -> list[tuple[Cell, Direction]]:
        """Walls in the order they were opened."""
        self._require_generated()
        return list(STUB_CARVE_HISTORY)

    @property
    def search_history(self) -> list[Cell]:
        """Cells in the order the solver explored them."""
        self._require_generated()
        return list(STUB_SEARCH_HISTORY)

    def _require_generated(self) -> None:
        """Raise MazeError if generate() was not called yet."""
        if not self._generated:
            raise MazeError("call generate() first")

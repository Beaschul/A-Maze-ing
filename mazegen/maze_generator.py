"""MazeGenerator: the interface between the core and the application.

``generate()`` blocks the "42" pattern, carves the maze with the chosen
algorithm, adds loops in Pac-Man mode (:mod:`mazegen.braid`) and finds the
shortest path (:mod:`mazegen.solver`). The application only reads the
results through the properties.
"""

import random
import secrets

from mazegen.algorithms import DEFAULT_ALGORITHM, get_carver
from mazegen.braid import braid
from mazegen.constants import MAX_DIMENSION, MIN_DIMENSION
from mazegen.directions import Direction
from mazegen.errors import MazeError
from mazegen.pattern import place_pattern
from mazegen.solver import Solution, solve
from mazegen.walls import Cell, WallGrid


class MazeGenerator:
    """Generate a maze and give read access to its structure and solution.

    Conventions:
        * Coordinates are ``(x, y)``: ``x`` = column, ``y`` = row. Grids
          are indexed ``grid[y][x]``.
        * Each cell is a 4-bit wall mask (see :mod:`mazegen.walls`).
        * Every problem raises :class:`~mazegen.errors.MazeError`. The
          package never prints, reads input or exits.
        * One instance = one seed = one maze. For a new maze, create a new
          instance.
        * Seed: all randomness comes from a private ``random.Random(seed)``,
          never from the global ``random`` module. When no seed is given,
          one is drawn and stored in :attr:`seed`, so the app can show it
          and the maze can be reproduced.
        * Algorithm: chosen by name (see
          :data:`mazegen.algorithms.ALGORITHMS`). Each one is a separate
          strategy with the same signature.
        * Replay data: :meth:`generate` records :attr:`carve_history` and
          :attr:`search_history`, so an application can replay the
          generation and the search (e.g. to animate them).

    Example::

        maze = MazeGenerator(20, 15, entry=(0, 0), exit=(19, 14), seed=42)
        maze.generate()
        maze.has_wall((0, 0), Direction.NORTH)  # True
        maze.solution_directions                 # "EESEN..."
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: Cell,
        exit: Cell,
        *,
        perfect: bool = True,
        seed: int | None = None,
        algorithm: str = DEFAULT_ALGORITHM,
    ) -> None:
        """Store the parameters of the maze.

        Args:
            width: Number of columns (see :mod:`mazegen.constants`).
            height: Number of rows (see :mod:`mazegen.constants`).
            entry: Entry cell ``(x, y)``.
            exit: Exit cell ``(x, y)``, different from ``entry``.
            perfect: True for exactly one path between entry and exit,
                False for a Pac-Man board (loops, few dead-ends).
            seed: Seed for reproducible mazes. None draws a random one,
                available afterwards in ``self.seed``.
            algorithm: Name of the generation algorithm, one of
                :data:`mazegen.algorithms.ALGORITHMS`.

        Raises:
            MazeError: If the size is out of bounds, entry/exit are
                outside the maze, equal, or on the "42" pattern, or the
                algorithm is unknown.
        """
        for name, size in (("width", width), ("height", height)):
            if not MIN_DIMENSION <= size <= MAX_DIMENSION:
                raise MazeError(
                    f"{name} must be between {MIN_DIMENSION} and "
                    f"{MAX_DIMENSION}, got {size}"
                )
        for name, (x, y) in (("entry", entry), ("exit", exit)):
            if not (0 <= x < width and 0 <= y < height):
                raise MazeError(
                    f"{name} ({x}, {y}) is outside the "
                    f"{width}x{height} maze"
                )
        if entry == exit:
            raise MazeError(f"entry and exit are the same cell {entry}")
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.perfect = perfect
        self.seed: int = secrets.randbits(32) if seed is None else seed
        self.algorithm = algorithm
        self._carve = get_carver(algorithm)
        self._walls: WallGrid | None = None
        self._carve_history: list[tuple[Cell, Direction]] = []
        self._solution: Solution | None = None
        self._pattern: set[Cell] = place_pattern(width, height)
        if entry in self._pattern:
            raise MazeError(f"entry {entry} is on the \"42\" pattern")
        if exit in self._pattern:
            raise MazeError(f"exit {exit} is on the \"42\" pattern")

    def generate(self) -> None:
        """Build the maze, its "42" pattern and its shortest path.

        The random generator is created here from :attr:`seed`, so calling
        it again rebuilds exactly the same maze.

        Raises:
            MazeError: If no valid maze exists for these parameters.
        """
        rng = random.Random(self.seed)
        walls = WallGrid(self.width, self.height)
        # Before carving: block() refuses a cell with an open wall.
        for cell in self._pattern:
            walls.block(cell)
        self._carve_history = self._carve(walls, rng, self.entry)
        if not self.perfect:
            self._carve_history += braid(walls, rng)
        self._solution = solve(walls, self.entry, self.exit)
        self._walls = walls

    def has_wall(self, cell: Cell, direction: Direction) -> bool:
        """Tell whether the wall ``direction`` of ``cell`` is closed.

        Raises:
            MazeError: If the cell is outside the maze, or generate() was
                not called yet.
        """
        walls = self._require_walls()
        if not walls.contains(cell):
            raise MazeError(f"cell {cell} is outside the maze")
        return walls.has_wall(cell, direction)

    @property
    def grid(self) -> list[list[int]]:
        """Copy of the wall masks, indexed ``grid[y][x]``."""
        return self._require_walls().to_lists()

    @property
    def pattern_cells(self) -> set[Cell]:
        """Cells drawing the "42" (empty if the maze is too small)."""
        return set(self._pattern)

    @property
    def solution(self) -> list[Cell]:
        """Cells of the shortest path, from entry to exit (inclusive)."""
        return list(self._require_solution().path)

    @property
    def solution_directions(self) -> str:
        """The shortest path written with the letters N, E, S and W."""
        return self._require_solution().directions

    @property
    def carve_history(self) -> list[tuple[Cell, Direction]]:
        """Walls in the order they were opened, e.g. to animate them."""
        self._require_walls()
        return list(self._carve_history)

    @property
    def search_history(self) -> list[Cell]:
        """Cells in the order the solver explored them, e.g. to animate."""
        return list(self._require_solution().history)

    def _require_walls(self) -> WallGrid:
        """Return the wall grid, or raise MazeError before generate()."""
        if self._walls is None:
            raise MazeError("call generate() first")
        return self._walls

    def _require_solution(self) -> Solution:
        """Return the solution, or raise MazeError before generate()."""
        if self._solution is None:
            raise MazeError("call generate() first")
        return self._solution

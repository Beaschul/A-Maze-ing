"""MazeGenerator: the interface between the core and the application.

Only the contract is defined here. Every method raises NotImplementedError
until its issue is done.
"""

from mazegen.directions import Direction
from mazegen.walls import Cell


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
        * Animations: :meth:`generate` records :attr:`carve_history` and
          :attr:`search_history`; the application replays them.

    Example::

        maze = MazeGenerator(20, 15, entry=(0, 0), exit=(19, 14), seed=42)
        maze.generate()
        maze.has_wall((0, 0), Direction.NORTH)  # True
        maze.solution_directions                 # "SSEN..."
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

        Raises:
            MazeError: If the size is out of bounds, or entry/exit are
                outside the maze, equal, or on the "42" pattern.
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.perfect = perfect
        self.seed = seed
        # TODO(#6): draw a seed when None, then create the private
        # random.Random(self.seed) used by the algorithms.

    def generate(self) -> None:
        """Build the maze, its "42" pattern and its shortest path.

        Raises:
            MazeError: If no valid maze exists for these parameters.
        """
        raise NotImplementedError

    def has_wall(self, cell: Cell, direction: Direction) -> bool:
        """Tell whether the wall ``direction`` of ``cell`` is closed.

        Raises:
            MazeError: If the cell is outside the maze.
        """
        raise NotImplementedError

    @property
    def grid(self) -> list[list[int]]:
        """Copy of the wall masks, indexed ``grid[y][x]``."""
        raise NotImplementedError

    @property
    def pattern_cells(self) -> set[Cell]:
        """Cells drawing the "42" (empty if the maze is too small)."""
        raise NotImplementedError

    @property
    def solution(self) -> list[Cell]:
        """Cells of the shortest path, from entry to exit (inclusive)."""
        raise NotImplementedError

    @property
    def solution_directions(self) -> str:
        """The shortest path written with the letters N, E, S and W."""
        raise NotImplementedError

    @property
    def carve_history(self) -> list[tuple[Cell, Direction]]:
        """Walls in the order they were opened, for the animation."""
        raise NotImplementedError

    @property
    def search_history(self) -> list[Cell]:
        """Cells in the order the solver explored them, for the animation."""
        raise NotImplementedError

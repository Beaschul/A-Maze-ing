"""Pac-Man board: add loops to a perfect maze ("braiding").

A perfect maze has no loop, so every dead-end is a trap for a chased
player. Braiding visits the dead-ends and opens one more wall in each:
the dead-end becomes a corridor and the maze gets a loop.

Rules for every wall it opens:
    * never on the outer border or a "42" cell (``grid.is_free``);
    * never a wall that would leave a 3x3 area with no wall inside it
      (:func:`~mazegen.validator.creates_open_area`);
    * preferably no small 2x2 room either, so corridors stay thin;
    * preferably towards another dead-end, which fixes both at once.

Some dead-ends cannot be fixed (stuck between the border and the "42", or
every option would open a 3x3 area): they are left as they are.
"""

import random

from mazegen.constants import MIN_LOOPS
from mazegen.directions import Direction
from mazegen.errors import MazeError
from mazegen.validator import (
    Wall,
    creates_open_area,
    dead_ends,
    free_cells,
    is_dead_end,
    loop_count,
)
from mazegen.walls import Cell, WallGrid, neighbour


def braid(grid: WallGrid, rng: random.Random) -> list[Wall]:
    """Open walls in a perfect maze until it is a Pac-Man board.

    Args:
        grid: Carved perfect maze, changed in place.
        rng: Source of every random choice.

    Returns:
        The opened walls, in order, as ``(cell, direction)``.

    Raises:
        MazeError: If the maze is too small to hold :data:`MIN_LOOPS`
            loops.
    """
    history: list[Wall] = []
    ends = dead_ends(grid)
    rng.shuffle(ends)
    for cell in ends:
        # A neighbour may already have opened into this one.
        if not is_dead_end(grid, cell):
            continue
        options = openable_walls(grid, cell)
        if options:
            d = best_wall(grid, cell, options, rng)
            grid.open_wall(cell, d)
            history.append((cell, d))
    _ensure_min_loops(grid, rng, history)
    return history


def openable_walls(grid: WallGrid, cell: Cell) -> list[Direction]:
    """Return the closed walls of ``cell`` that braiding may open.

    Args:
        grid: Maze to inspect.
        cell: Free cell ``(x, y)``.

    Returns:
        The sides facing a free cell whose opening does not create an open
        3x3 area.
    """
    return [
        d for d in Direction
        if grid.has_wall(cell, d)
        and grid.is_free(neighbour(cell, d))
        and not creates_open_area(grid, cell, d)
    ]


def score(grid: WallGrid, cell: Cell, d: Direction) -> int:
    """Rate how nice opening wall ``d`` of ``cell`` would look.

    Args:
        grid: Maze to inspect.
        cell: Position ``(x, y)`` of the wall.
        d: Side of ``cell`` the wall is on.

    Returns:
        +2 if no 2x2 room appears (thin corridors), +1 if the neighbour is
        a dead-end too (two fixed at once).
    """
    points = 0
    if not creates_open_area(grid, cell, d, size=2):
        points += 2
    if is_dead_end(grid, neighbour(cell, d)):
        points += 1
    return points


def best_wall(grid: WallGrid, cell: Cell, options: list[Direction],
              rng: random.Random) -> Direction:
    """Pick the option with the best :func:`score`, ties broken at random.

    Args:
        grid: Maze to inspect.
        cell: Position ``(x, y)`` of the walls.
        options: Sides to choose from, not empty.
        rng: Source of the random tie-break.

    Returns:
        The chosen side.
    """
    shuffled = options[:]
    rng.shuffle(shuffled)
    # max() keeps the first of the best: the shuffle decides which one.
    return max(shuffled, key=lambda d: score(grid, cell, d))


def _ensure_min_loops(grid: WallGrid, rng: random.Random,
                      history: list[Wall]) -> None:
    """Open random walls until the maze has :data:`MIN_LOOPS` loops.

    Only needed on tiny mazes, where braiding found too few dead-ends.

    Raises:
        MazeError: If no wall can be opened anymore.
    """
    while loop_count(grid) < MIN_LOOPS:
        candidates = [
            (cell, d)
            for cell in free_cells(grid)
            for d in (Direction.EAST, Direction.SOUTH)
            if grid.has_wall(cell, d)
            and grid.is_free(neighbour(cell, d))
            and not creates_open_area(grid, cell, d)
        ]
        if not candidates:
            raise MazeError(
                f"a {grid.width}x{grid.height} maze is too small for a "
                f"Pac-Man board ({MIN_LOOPS} loops needed)")
        rng.shuffle(candidates)
        cell, d = max(candidates, key=lambda wall: score(grid, *wall))
        grid.open_wall(cell, d)
        history.append((cell, d))

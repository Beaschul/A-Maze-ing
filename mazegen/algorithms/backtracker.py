"""Recursive backtracker (randomized depth-first search).

It walks from the start cell to a random unvisited neighbour, opening the
wall between them, and backs up when it reaches a dead-end. The result has
long corridors and few branches.

The "recursion" is an explicit stack: Python's recursion limit (~1000)
would break on big mazes.
"""

import random

from mazegen.directions import Direction
from mazegen.walls import Cell, WallGrid, neighbour


def carve_backtracker(grid: WallGrid, rng: random.Random,
                      start: Cell) -> list[tuple[Cell, Direction]]:
    """Carve a perfect maze into ``grid`` with a depth-first search.

    Args:
        grid: Fully closed grid; blocked cells are never entered.
        rng: Source of every random choice.
        start: Free cell the search starts from.

    Returns:
        The opened walls, in order, as ``(cell, direction)``.
    """
    history: list[tuple[Cell, Direction]] = []
    visited: set[Cell] = {start}
    stack: list[Cell] = [start]
    while stack:
        cell = stack[-1]
        options = [
            d for d in Direction
            if neighbour(cell, d) not in visited
            and grid.is_free(neighbour(cell, d))
        ]
        if not options:
            stack.pop()
            continue
        d = rng.choice(options)
        grid.open_wall(cell, d)
        history.append((cell, d))
        nxt = neighbour(cell, d)
        visited.add(nxt)
        stack.append(nxt)
    return history

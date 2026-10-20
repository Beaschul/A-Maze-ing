"""Shortest path between two cells (breadth-first search).

The search spreads from the start one layer at a time: first every cell 1
step away, then every cell 2 steps away, and so on. The queue (FIFO) is what
gives that order. Every step costs the same, so the first time the search
reaches the goal it got there by a shortest path.

Each cell is discovered only once: the first discovery is the closest one,
and any later (longer) way to reach it is ignored. That also stops the
search from walking back or looping in Pac-Man mazes.

No recursion is used, so big mazes are safe.
"""

from collections import deque
from dataclasses import dataclass

from mazegen.directions import LETTER, Direction
from mazegen.errors import MazeError
from mazegen.walls import Cell, WallGrid, neighbour


@dataclass(frozen=True)
class Solution:
    """Result of :func:`solve`.

    Attributes:
        path: Cells from the start to the goal, both included.
        directions: The same path as the letters N, E, S and W.
        history: Cells in the order they left the queue, for the search
            animation.
    """

    path: list[Cell]
    directions: str
    history: list[Cell]


def solve(grid: WallGrid, start: Cell, goal: Cell) -> Solution:
    """Find a shortest path from ``start`` to ``goal`` through open walls.

    Args:
        grid: Carved maze.
        start: Cell the search starts from (the entry).
        goal: Cell to reach (the exit).

    Returns:
        The path, its letters and the search order.

    Raises:
        MazeError: If ``goal`` cannot be reached from ``start``.
    """
    # parents[cell] = (previous cell, step taken from it).
    # A cell is in parents once it has been discovered.
    parents: dict[Cell, tuple[Cell, Direction] | None] = {start: None}
    queue: deque[Cell] = deque([start])
    history: list[Cell] = []
    while queue:
        cell = queue.popleft()
        history.append(cell)
        if cell == goal:
            break
        for d in Direction:
            nxt = neighbour(cell, d)
            # The outer border is always closed, so nxt is inside the grid.
            if not grid.has_wall(cell, d) and nxt not in parents:
                parents[nxt] = (cell, d)
                queue.append(nxt)
    else:
        raise MazeError(f"no path from {start} to {goal}")

    # Walk back from the goal following the parents, then reverse.
    path: list[Cell] = [goal]
    letters: list[str] = []
    step = parents[goal]
    while step is not None:
        prev, d = step
        path.append(prev)
        letters.append(LETTER[d])
        step = parents[prev]
    path.reverse()
    letters.reverse()
    return Solution(path, "".join(letters), history)

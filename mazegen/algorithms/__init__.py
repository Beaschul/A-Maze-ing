"""Maze generation algorithms (Strategy pattern).

Every algorithm is a function with the :data:`Carver` signature: it receives
a fully closed :class:`~mazegen.walls.WallGrid` (with the "42" already
blocked), the private random generator and the start cell, and opens walls
until every free cell is reachable from the start, without any loop (a
spanning tree). It returns the opened walls in order, for the animation.

The generator only looks the algorithm up by name, so adding one is a new
function plus one entry in :data:`_CARVERS`.
"""

import random
from collections.abc import Callable

from mazegen.algorithms.backtracker import carve_backtracker
from mazegen.directions import Direction
from mazegen.errors import MazeError
from mazegen.walls import Cell, WallGrid

Carver = Callable[
    [WallGrid, random.Random, Cell], list[tuple[Cell, Direction]]
]
"""Signature shared by every algorithm: ``(grid, rng, start) -> history``."""

_CARVERS: dict[str, Carver] = {
    "backtracker": carve_backtracker,
}

ALGORITHMS: tuple[str, ...] = tuple(_CARVERS)
"""Names accepted by ``MazeGenerator(algorithm=...)``."""

DEFAULT_ALGORITHM: str = "backtracker"
"""Algorithm used when none is given."""


def get_carver(name: str) -> Carver:
    """Return the algorithm called ``name``.

    Args:
        name: One of :data:`ALGORITHMS`.

    Returns:
        The carving function.

    Raises:
        MazeError: If no algorithm has this name.
    """
    try:
        return _CARVERS[name]
    except KeyError:
        choices = ", ".join(ALGORITHMS)
        raise MazeError(
            f"unknown algorithm {name!r} (choose from: {choices})"
        ) from None

"""mazegen: reusable maze generation package.

This package is distributed on its own (``mazegen-*.whl``) to be reused by
later projects, so it must stay independent from the application: it never
imports ``app``, never prints, never reads user input and never exits.
Errors are reported with exceptions.
"""

from mazegen.constants import MAX_DIMENSION, MIN_DIMENSION
from mazegen.directions import Direction
from mazegen.errors import MazeError
from mazegen.maze_generator import MazeGenerator
from mazegen.walls import ALL_WALLS, Cell

__all__ = [
    "ALL_WALLS",
    "MAX_DIMENSION",
    "MIN_DIMENSION",
    "Cell",
    "Direction",
    "MazeError",
    "MazeGenerator",
]

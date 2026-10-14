"""Cells, directions and wall bits.

Coordinates are ``(x, y)``: ``x`` is the column (0 = left) and ``y`` is the
row (0 = top). Grids are always indexed ``grid[y][x]``.

Each cell stores its closed walls as a 4-bit mask (1 = closed)::

    bit 0  NORTH  1
    bit 1  EAST   2
    bit 2  SOUTH  4
    bit 3  WEST   8
"""

from enum import IntFlag

Cell = tuple[int, int]
"""A cell position ``(x, y)``."""


class Direction(IntFlag):
    """Cardinal direction, valued with its wall bit."""

    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8


ALL_WALLS: int = 0xF
"""Wall mask of a fully closed cell."""

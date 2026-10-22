"""Cardinal directions and their lookup tables.

Each direction is valued with its wall bit (1 = closed)::

    bit 0  NORTH  1
    bit 1  EAST   2
    bit 2  SOUTH  4
    bit 3  WEST   8

``y`` grows downwards (row 0 is the top), so NORTH moves to ``y - 1``.
"""

from enum import IntFlag


class Direction(IntFlag):
    """Cardinal direction, valued with its wall bit."""

    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8


DELTA: dict[Direction, tuple[int, int]] = {
    Direction.NORTH: (0, -1),
    Direction.EAST: (1, 0),
    Direction.SOUTH: (0, 1),
    Direction.WEST: (-1, 0),
}
"""Offset ``(dx, dy)`` to the neighbour in each direction."""

OPPOSITE: dict[Direction, Direction] = {
    Direction.NORTH: Direction.SOUTH,
    Direction.EAST: Direction.WEST,
    Direction.SOUTH: Direction.NORTH,
    Direction.WEST: Direction.EAST,
}
"""Direction pointing back from the neighbour."""

LETTER: dict[Direction, str] = {
    Direction.NORTH: "N",
    Direction.EAST: "E",
    Direction.SOUTH: "S",
    Direction.WEST: "W",
}
"""Single-letter name used in the path output."""

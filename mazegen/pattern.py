"""Placement of the "42" pattern.

The pattern is the bitmap :data:`~mazegen.constants.PATTERN_42`, centred in
the maze. Its cells stay fully closed: the generator blocks them before
carving, so no algorithm ever opens their walls.

The pattern is always centred, even in Pac-Man mode (``perfect=False``),
where the player starts at the centre: the start cell is then the open cell
closest to the centre.
"""

from mazegen.constants import (
    PATTERN_42,
    PATTERN_MIN_HEIGHT,
    PATTERN_MIN_WIDTH,
)
from mazegen.walls import Cell


def fits_pattern(width: int, height: int) -> bool:
    """Tell whether a ``width`` x ``height`` maze can hold the pattern.

    Args:
        width: Number of columns.
        height: Number of rows.

    Returns:
        True if the pattern and its margin fit, False otherwise.
    """
    return width >= PATTERN_MIN_WIDTH and height >= PATTERN_MIN_HEIGHT


def place_pattern(width: int, height: int) -> set[Cell]:
    """Return the cells of the "42" pattern centred in the maze.

    Args:
        width: Number of columns.
        height: Number of rows.

    Returns:
        The ``(x, y)`` cells drawing the pattern, or an empty set if the
        maze is too small (see :func:`fits_pattern`).
    """
    if not fits_pattern(width, height):
        return set()
    offset_x = (width - len(PATTERN_42[0])) // 2
    offset_y = (height - len(PATTERN_42)) // 2
    return {
        (offset_x + col, offset_y + row)
        for row, line in enumerate(PATTERN_42)
        for col, char in enumerate(line)
        if char == "#"
    }

"""Limits and fixed values shared by the package and the application."""

MIN_DIMENSION: int = 2
"""Smallest accepted WIDTH / HEIGHT."""

MAX_DIMENSION: int = 500
"""Largest accepted WIDTH / HEIGHT (avoids huge allocations)."""

PATTERN_42: tuple[str, ...] = (
    "#...###",
    "#.....#",
    "###.###",
    "..#.#..",
    "..#.###",
)
"""Bitmap of the "42" pattern ('#' = fully closed cell, '.' = free cell)."""

PATTERN_MARGIN: int = 1
"""Free cells kept around the pattern so no cell gets isolated."""

PATTERN_MIN_WIDTH: int = len(PATTERN_42[0]) + 2 * PATTERN_MARGIN
"""Smallest WIDTH that fits the "42" pattern plus its margin."""

PATTERN_MIN_HEIGHT: int = len(PATTERN_42) + 2 * PATTERN_MARGIN
"""Smallest HEIGHT that fits the "42" pattern plus its margin."""

MIN_LOOPS: int = 2
"""Independent loops a Pac-Man board (PERFECT=False) must have at least."""

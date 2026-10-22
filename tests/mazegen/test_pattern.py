"""Tests for the placement of the "42" pattern.

They cover the size limit, the centring and the margin left around the
pattern.
"""

import pytest

from mazegen.constants import (
    PATTERN_42,
    PATTERN_MARGIN,
    PATTERN_MIN_HEIGHT,
    PATTERN_MIN_WIDTH,
)
from mazegen.pattern import fits_pattern, place_pattern

PATTERN_SIZE = sum(line.count("#") for line in PATTERN_42)


def test_smallest_maze_fits() -> None:
    assert fits_pattern(PATTERN_MIN_WIDTH, PATTERN_MIN_HEIGHT)
    assert len(place_pattern(PATTERN_MIN_WIDTH,
                             PATTERN_MIN_HEIGHT)) == PATTERN_SIZE


@pytest.mark.parametrize(
    ("width", "height"),
    [
        (PATTERN_MIN_WIDTH - 1, PATTERN_MIN_HEIGHT),
        (PATTERN_MIN_WIDTH, PATTERN_MIN_HEIGHT - 1),
        (2, 2),
    ],
)
def test_too_small_maze_has_no_pattern(width: int, height: int) -> None:
    assert not fits_pattern(width, height)
    assert place_pattern(width, height) == set()


def test_pattern_matches_bitmap() -> None:
    # In the smallest maze the bitmap starts right after the margin.
    cells = place_pattern(PATTERN_MIN_WIDTH, PATTERN_MIN_HEIGHT)
    for row, line in enumerate(PATTERN_42):
        for col, char in enumerate(line):
            cell = (PATTERN_MARGIN + col, PATTERN_MARGIN + row)
            assert (cell in cells) == (char == "#")


def test_pattern_is_centred() -> None:
    # Non-square maze: swapping x and y would shift the pattern.
    cells = place_pattern(21, 11)
    xs = [x for x, _ in cells]
    ys = [y for _, y in cells]
    assert (min(xs), max(xs)) == (7, 13)
    assert (min(ys), max(ys)) == (3, 7)


@pytest.mark.parametrize(("width", "height"),
                         [(9, 7), (10, 8), (20, 15), (500, 500)])
def test_pattern_keeps_margin(width: int, height: int) -> None:
    for x, y in place_pattern(width, height):
        assert PATTERN_MARGIN <= x < width - PATTERN_MARGIN
        assert PATTERN_MARGIN <= y < height - PATTERN_MARGIN

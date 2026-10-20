"""Tests for the MazeGenerator interface.

Only the parts already implemented are covered: the "42" pattern cells and
the entry/exit check against them.
"""

import pytest

from mazegen.errors import MazeError
from mazegen.maze_generator import MazeGenerator
from mazegen.pattern import place_pattern

# A cell of the pattern in a 20x15 maze: top of the left leg of the "4".
ON_PATTERN = min(place_pattern(20, 15))


def test_pattern_cells_match_placement() -> None:
    maze = MazeGenerator(20, 15, (0, 0), (19, 14))
    assert maze.pattern_cells == place_pattern(20, 15)


def test_pattern_cells_empty_when_too_small() -> None:
    maze = MazeGenerator(5, 5, (0, 0), (4, 4))
    assert maze.pattern_cells == set()


def test_pattern_cells_returns_a_copy() -> None:
    maze = MazeGenerator(20, 15, (0, 0), (19, 14))
    maze.pattern_cells.clear()
    assert maze.pattern_cells == place_pattern(20, 15)


def test_entry_on_pattern_raises() -> None:
    with pytest.raises(MazeError, match="entry"):
        MazeGenerator(20, 15, ON_PATTERN, (19, 14))


def test_exit_on_pattern_raises() -> None:
    with pytest.raises(MazeError, match="exit"):
        MazeGenerator(20, 15, (0, 0), ON_PATTERN)

"""Tests for the MazeGenerator interface.

Only the parts already implemented are covered: the constructor checks
(size, entry/exit inside the grid, different, off the "42" pattern), the
"42" pattern cells and the solution properties.
"""

import pytest

from mazegen.constants import MAX_DIMENSION, MIN_DIMENSION
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


@pytest.mark.parametrize(
    ("width", "height", "match"),
    [
        (MIN_DIMENSION - 1, 15, "width"),
        (MAX_DIMENSION + 1, 15, "width"),
        (20, MIN_DIMENSION - 1, "height"),
        (20, MAX_DIMENSION + 1, "height"),
    ],
)
def test_size_out_of_bounds_raises(
    width: int, height: int, match: str
) -> None:
    with pytest.raises(MazeError, match=match):
        MazeGenerator(width, height, (0, 0), (1, 1))


def test_size_at_bounds_is_accepted() -> None:
    MazeGenerator(MIN_DIMENSION, MIN_DIMENSION, (0, 0), (1, 1))
    MazeGenerator(MAX_DIMENSION, MAX_DIMENSION, (0, 0), (1, 1))


@pytest.mark.parametrize(
    ("entry", "exit", "match"),
    [
        ((-1, 0), (19, 14), "entry"),
        ((20, 0), (19, 14), "entry"),
        ((0, 15), (19, 14), "entry"),
        ((0, 0), (0, -1), "exit"),
        ((0, 0), (20, 14), "exit"),
        ((0, 0), (19, 15), "exit"),
    ],
)
def test_entry_exit_outside_raises(
    entry: tuple[int, int], exit: tuple[int, int], match: str
) -> None:
    with pytest.raises(MazeError, match=f"{match} .* outside"):
        MazeGenerator(20, 15, entry, exit)


def test_entry_equals_exit_raises() -> None:
    with pytest.raises(MazeError, match="same cell"):
        MazeGenerator(20, 15, (3, 3), (3, 3))


def test_solution_before_generate_raises() -> None:
    maze = MazeGenerator(20, 15, (0, 0), (19, 14), seed=42)
    with pytest.raises(MazeError):
        maze.solution
    with pytest.raises(MazeError):
        maze.solution_directions
    with pytest.raises(MazeError):
        maze.search_history


def test_solution_goes_from_entry_to_exit() -> None:
    maze = MazeGenerator(20, 15, (0, 0), (19, 14), seed=42)
    maze.generate()
    assert maze.solution[0] == (0, 0)
    assert maze.solution[-1] == (19, 14)
    assert len(maze.solution) == len(maze.solution_directions) + 1


def test_search_history_starts_at_entry_and_ends_at_exit() -> None:
    maze = MazeGenerator(20, 15, (0, 0), (19, 14), seed=42)
    maze.generate()
    assert maze.search_history[0] == (0, 0)
    assert maze.search_history[-1] == (19, 14)


def test_same_seed_gives_same_solution() -> None:
    first = MazeGenerator(20, 15, (0, 0), (19, 14), seed=42)
    second = MazeGenerator(20, 15, (0, 0), (19, 14), seed=42)
    first.generate()
    second.generate()
    assert first.solution_directions == second.solution_directions

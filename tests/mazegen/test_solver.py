"""Tests for the shortest path solver.

The mazes are built by hand: they are the examples of the README.
"""

from dataclasses import FrozenInstanceError

import pytest

from mazegen.directions import Direction
from mazegen.errors import MazeError
from mazegen.solver import solve
from mazegen.walls import WallGrid

N, E, S, W = Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST


def readme_maze() -> WallGrid:
    """The 3x2 perfect maze of the README::

        +---+---+---+
        | A     | B |
        +---+   +   +
        |           |
        +---+---+---+
    """
    walls = WallGrid(3, 2)
    walls.open_wall((0, 0), E)
    walls.open_wall((1, 0), S)
    walls.open_wall((1, 1), W)
    walls.open_wall((1, 1), E)
    walls.open_wall((2, 1), N)
    return walls


def ring_maze() -> WallGrid:
    """A 3x2 ring: two routes from A to B, ``EE`` and ``SEEN``::

        +---+---+---+
        | A       B |
        +   +---+   +
        |           |
        +---+---+---+
    """
    walls = WallGrid(3, 2)
    walls.open_wall((0, 0), E)
    walls.open_wall((1, 0), E)
    walls.open_wall((0, 0), S)
    walls.open_wall((0, 1), E)
    walls.open_wall((1, 1), E)
    walls.open_wall((2, 1), N)
    return walls


def test_readme_example() -> None:
    sol = solve(readme_maze(), (0, 0), (2, 0))
    assert sol.directions == "ESEN"
    assert sol.path == [(0, 0), (1, 0), (1, 1), (2, 1), (2, 0)]


def test_readme_example_history() -> None:
    # Same order as the "Tira" column of the README table.
    sol = solve(readme_maze(), (0, 0), (2, 0))
    assert sol.history == [(0, 0), (1, 0), (1, 1), (2, 1), (0, 1), (2, 0)]


def test_ring_takes_the_shortest_route() -> None:
    sol = solve(ring_maze(), (0, 0), (2, 0))
    assert sol.directions == "EE"
    assert sol.path == [(0, 0), (1, 0), (2, 0)]


def test_path_has_one_more_cell_than_letters() -> None:
    sol = solve(readme_maze(), (0, 0), (2, 0))
    assert len(sol.path) == len(sol.directions) + 1


def test_solution_is_frozen() -> None:
    sol = solve(readme_maze(), (0, 0), (2, 0))
    with pytest.raises(FrozenInstanceError):
        sol.directions = "NNNN"  # type: ignore[misc]


def test_unreachable_goal_raises() -> None:
    walls = WallGrid(3, 2)
    walls.open_wall((0, 0), E)
    with pytest.raises(MazeError):
        solve(walls, (0, 0), (2, 1))

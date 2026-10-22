"""Tests for the Pac-Man board, PERFECT=False (#12).

Every generated board must be connected, have at least MIN_LOOPS loops,
almost no dead-end and no open 3x3 area, for many seeds and sizes.
"""

import random

import pytest

from mazegen.algorithms import ALGORITHMS
from mazegen.braid import best_wall, openable_walls
from mazegen.constants import MIN_LOOPS
from mazegen.directions import Direction
from mazegen.errors import MazeError
from mazegen.maze_generator import MazeGenerator
from mazegen.validator import (
    dead_ends,
    has_open_3x3,
    is_connected,
    loop_count,
)
from mazegen.walls import Cell, WallGrid, neighbour
from tests.mazegen.test_validator import open_room, to_wall_grid

N, E, S, W = (Direction.NORTH, Direction.EAST,
              Direction.SOUTH, Direction.WEST)

SIZES = [(3, 3), (5, 5), (9, 7), (20, 15), (31, 21)]

MAX_REAL_DEAD_ENDS = 2
"""Same tolerance as the default of maze_analyzer.py."""


def make(width: int, height: int, seed: int, perfect: bool = False,
         algorithm: str = "backtracker") -> MazeGenerator:
    """Build and generate a maze, entry and exit in opposite corners."""
    maze = MazeGenerator(width, height, (0, 0), (width - 1, height - 1),
                         perfect=perfect, seed=seed, algorithm=algorithm)
    maze.generate()
    return maze


def real_dead_ends(walls: WallGrid) -> list[Cell]:
    """Dead-ends with a closed wall that could have been opened.

    The other ones only face the border or the "42": nothing to fix.
    """
    return [
        cell for cell in dead_ends(walls)
        if any(walls.has_wall(cell, d) and walls.is_free(neighbour(cell, d))
               for d in Direction)
    ]


# --- whole boards --------------------------------------------------------


@pytest.mark.parametrize("algorithm", ALGORITHMS)
@pytest.mark.parametrize("width, height", SIZES)
@pytest.mark.parametrize("seed", range(100))
def test_pacman_board(algorithm: str, width: int, height: int,
                      seed: int) -> None:
    maze = make(width, height, seed, algorithm=algorithm)
    walls = to_wall_grid(maze)
    assert walls.to_lists() == maze.grid        # both sides of walls agree
    assert is_connected(walls)
    assert loop_count(walls) >= MIN_LOOPS
    assert not has_open_3x3(walls)
    assert len(real_dead_ends(walls)) <= MAX_REAL_DEAD_ENDS


def test_same_seed_same_board() -> None:
    assert make(20, 15, seed=7).grid == make(20, 15, seed=7).grid


def test_different_seed_different_board() -> None:
    assert make(20, 15, seed=1).grid != make(20, 15, seed=2).grid


def test_perfect_maze_is_not_braided() -> None:
    assert loop_count(to_wall_grid(make(20, 15, seed=7, perfect=True))) == 0


def test_braid_starts_from_the_perfect_maze() -> None:
    # Same seed: the board is the perfect maze plus the braided walls, one
    # new loop per wall, all recorded for the animation.
    perfect = make(20, 15, seed=7, perfect=True)
    board = make(20, 15, seed=7)
    carved = len(perfect.carve_history)
    assert board.carve_history[:carved] == perfect.carve_history
    extra = len(board.carve_history) - carved
    assert extra == loop_count(to_wall_grid(board))


def test_board_still_has_a_solution() -> None:
    maze = make(20, 15, seed=7)
    assert maze.solution[0] == (0, 0)
    assert maze.solution[-1] == (19, 14)


def test_too_small_for_a_board() -> None:
    # 2x2: at most one loop (the 4 cells in a ring).
    with pytest.raises(MazeError, match="too small"):
        make(2, 2, seed=7)


# --- single steps --------------------------------------------------------


def test_openable_walls_skip_the_border() -> None:
    assert openable_walls(WallGrid(2, 2), (0, 0)) == [E, S]


def test_openable_walls_skip_blocked_cells() -> None:
    walls = WallGrid(2, 2)
    walls.block((1, 0))
    assert openable_walls(walls, (0, 0)) == [S]


def test_openable_walls_skip_open_3x3() -> None:
    walls = open_room(3, 3, skip=((1, 1), E))
    assert E not in openable_walls(walls, (1, 1))
    assert W not in openable_walls(walls, (2, 1))


@pytest.mark.parametrize("seed", range(10))
def test_best_wall_prefers_another_dead_end(seed: int) -> None:
    # +--+--+--+
    # |  |  |  |    (0, 0) is a dead-end (open to the south),
    # +  +--+--+    (2, 0) is fully closed: (1, 0) should open west.
    # |  |  |  |
    # +--+--+--+
    walls = WallGrid(3, 2)
    walls.open_wall((0, 0), S)
    assert best_wall(walls, (1, 0), [E, W], random.Random(seed)) == W


@pytest.mark.parametrize("seed", range(10))
def test_best_wall_avoids_2x2_rooms(seed: int) -> None:
    # The 2x2 on the left only misses the wall (0, 0) E: opening it makes
    # a small room, so (1, 0) should open east instead.
    walls = WallGrid(3, 2)
    walls.open_wall((0, 0), S)
    walls.open_wall((0, 1), E)
    walls.open_wall((1, 1), N)
    assert best_wall(walls, (1, 0), [E, W], random.Random(seed)) == E

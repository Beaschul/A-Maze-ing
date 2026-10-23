"""Tests for the maze checks (#13).

Most mazes are built by hand: start from a closed WallGrid and open the
walls one by one, so the expected answer can be counted on paper. The last
tests run the checks on real perfect mazes.
"""

import pytest

from mazegen.algorithms import ALGORITHMS
from mazegen.directions import Direction
from mazegen.maze_generator import MazeGenerator
from mazegen.validator import (
    count_components,
    count_passages,
    creates_open_area,
    dead_ends,
    free_cells,
    has_open_3x3,
    is_connected,
    is_dead_end,
    loop_count,
    window_is_open,
)
from mazegen.walls import Cell, WallGrid

E, S, W = Direction.EAST, Direction.SOUTH, Direction.WEST


def open_room(width: int, height: int,
              skip: tuple[Cell, Direction] | None = None) -> WallGrid:
    """Return a grid with every inner wall open, except ``skip``."""
    walls = WallGrid(width, height)
    for y in range(height):
        for x in range(width):
            for d in (E, S):
                if ((x, y), d) == skip:
                    continue
                if (d == E and x < width - 1) or (d == S and y < height - 1):
                    walls.open_wall((x, y), d)
    return walls


def to_wall_grid(maze: MazeGenerator) -> WallGrid:
    """Rebuild the WallGrid of a generated maze from its public grid."""
    walls = WallGrid(maze.width, maze.height)
    for cell in maze.pattern_cells:
        walls.block(cell)
    for y, row in enumerate(maze.grid):
        for x, mask in enumerate(row):
            for d in (E, S):
                if not mask & d:
                    walls.open_wall((x, y), d)
    return walls


# --- free cells and dead-ends --------------------------------------------


def test_free_cells_skip_blocked_cells() -> None:
    walls = WallGrid(2, 2)
    walls.block((1, 1))
    assert free_cells(walls) == [(0, 0), (1, 0), (0, 1)]


def test_dead_ends_of_a_corridor() -> None:
    # +--+--+--+
    # |        |   (0, 0) and (2, 0) have one opening; (1, 0) has two.
    # +--+--+--+
    walls = WallGrid(3, 1)
    walls.open_wall((0, 0), E)
    walls.open_wall((1, 0), E)
    assert dead_ends(walls) == [(0, 0), (2, 0)]
    assert not is_dead_end(walls, (1, 0))


def test_closed_cell_is_not_a_dead_end() -> None:
    # 4 closed walls: isolated, not a dead-end (that needs exactly 3).
    walls = WallGrid(2, 1)
    assert dead_ends(walls) == []


def test_blocked_cell_is_not_a_dead_end() -> None:
    walls = WallGrid(3, 1)
    walls.block((1, 0))
    assert not is_dead_end(walls, (1, 0))


# --- connectivity --------------------------------------------------------


def test_closed_grid_has_one_island_per_cell() -> None:
    walls = WallGrid(2, 2)
    assert count_components(walls) == 4
    assert not is_connected(walls)


def test_opening_a_wall_joins_two_islands() -> None:
    walls = WallGrid(2, 2)
    walls.open_wall((0, 0), E)
    assert count_components(walls) == 3


def test_open_room_is_connected() -> None:
    assert count_components(open_room(4, 3)) == 1
    assert is_connected(open_room(4, 3))


def test_blocked_cells_are_not_islands() -> None:
    # (0, 0) - (1, 0) - (2, 0) with the middle one blocked: 2 islands,
    # the blocked cell is not counted as a third one.
    walls = WallGrid(3, 1)
    walls.block((1, 0))
    assert count_components(walls) == 2


# --- passages and loops --------------------------------------------------


def test_closed_grid_has_no_passage() -> None:
    assert count_passages(WallGrid(3, 3)) == 0


def test_open_room_passages() -> None:
    # 3x3: 2 EAST walls x 3 rows + 2 SOUTH walls x 3 columns.
    assert count_passages(open_room(3, 3)) == 12


def test_corridor_has_no_loop() -> None:
    walls = WallGrid(3, 1)
    walls.open_wall((0, 0), E)
    walls.open_wall((1, 0), E)
    assert loop_count(walls) == 0


def test_ring_of_four_cells_has_one_loop() -> None:
    # 4 passages - 4 cells + 1 island = 1
    assert loop_count(open_room(2, 2)) == 1


def test_open_3x3_room_has_four_loops() -> None:
    # 12 passages - 9 cells + 1 island = 4 (the four small 2x2 squares)
    assert loop_count(open_room(3, 3)) == 4


def test_two_separate_trees_have_no_loop() -> None:
    # Two corridors that do not touch: 2 passages - 4 cells + 2 islands.
    walls = WallGrid(2, 2)
    walls.open_wall((0, 0), E)
    walls.open_wall((0, 1), E)
    assert loop_count(walls) == 0


# --- windows and open 3x3 areas ------------------------------------------


def test_open_window() -> None:
    assert window_is_open(open_room(3, 3), 0, 0, 3)


def test_window_with_one_inner_wall_is_not_open() -> None:
    walls = open_room(3, 3, skip=((1, 1), E))
    assert not window_is_open(walls, 0, 0, 3)


def test_window_outside_the_grid_is_not_open() -> None:
    walls = open_room(3, 3)
    assert not window_is_open(walls, 1, 0, 3)
    assert not window_is_open(walls, -1, 0, 3)


def test_window_ignores_its_border() -> None:
    # 4x3 grid: the 3x3 on the left is open, the last column is walled
    # off. The wall on the window's right edge does not count.
    walls = WallGrid(4, 3)
    for y in range(3):
        for x in range(3):
            if x < 2:
                walls.open_wall((x, y), E)
            if y < 2:
                walls.open_wall((x, y), S)
    assert window_is_open(walls, 0, 0, 3)
    assert not window_is_open(walls, 1, 0, 3)


def test_pretend_open_counts_the_wall_as_open() -> None:
    walls = open_room(3, 3, skip=((1, 1), E))
    assert window_is_open(walls, 0, 0, 3, pretend_open=((1, 1), E))


def test_has_open_3x3() -> None:
    assert has_open_3x3(open_room(3, 3))
    assert has_open_3x3(open_room(5, 4))


def test_no_open_3x3() -> None:
    assert not has_open_3x3(WallGrid(5, 5))
    assert not has_open_3x3(open_room(2, 5))
    assert not has_open_3x3(open_room(3, 3, skip=((0, 0), S)))


# --- creates_open_area: "what if I open this wall?" ----------------------


@pytest.mark.parametrize("missing", [
    ((1, 1), E), ((0, 0), S), ((1, 0), E), ((2, 1), S),
])
def test_last_missing_wall_creates_open_area(
        missing: tuple[Cell, Direction]) -> None:
    walls = open_room(3, 3, skip=missing)
    cell, d = missing
    assert creates_open_area(walls, cell, d)


def test_same_wall_from_both_sides() -> None:
    # The EAST wall of (1, 1) is the WEST wall of (2, 1).
    walls = open_room(3, 3, skip=((1, 1), E))
    assert creates_open_area(walls, (1, 1), E)
    assert creates_open_area(walls, (2, 1), W)


def test_wall_that_does_not_complete_a_room() -> None:
    # Two walls missing: opening one of them still leaves the other.
    walls = WallGrid(3, 3)
    for y in range(3):
        for x in range(3):
            if x < 2 and (x, y) not in ((1, 1), (0, 2)):
                walls.open_wall((x, y), E)
            if y < 2:
                walls.open_wall((x, y), S)
    assert not creates_open_area(walls, (1, 1), E)


def test_creates_open_area_does_not_change_the_grid() -> None:
    walls = open_room(3, 3, skip=((1, 1), E))
    before = walls.to_lists()
    creates_open_area(walls, (1, 1), E)
    assert walls.to_lists() == before


def test_creates_open_2x2_area() -> None:
    walls = open_room(2, 2, skip=((0, 0), E))
    assert creates_open_area(walls, (0, 0), E, size=2)
    assert not creates_open_area(walls, (0, 0), E, size=3)


# --- real mazes ----------------------------------------------------------


@pytest.mark.parametrize("algorithm", ALGORITHMS)
@pytest.mark.parametrize("width, height", [(5, 5), (20, 15), (31, 9)])
@pytest.mark.parametrize("seed", range(10))
def test_perfect_maze_checks(algorithm: str, width: int, height: int,
                             seed: int) -> None:
    maze = MazeGenerator(width, height, (0, 0), (width - 1, height - 1),
                         seed=seed, algorithm=algorithm)
    maze.generate()
    walls = to_wall_grid(maze)
    assert is_connected(walls)
    assert loop_count(walls) == 0
    assert not has_open_3x3(walls)
    assert dead_ends(walls)

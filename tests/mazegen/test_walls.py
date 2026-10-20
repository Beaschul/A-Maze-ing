"""Tests for the wall grid.

They cover the coherence rule (opening a wall updates both neighbours),
the closed outer border, the x/y orientation of the grid and the blocked
cells of the "42" pattern.
"""

import pytest

from mazegen.directions import Direction
from mazegen.walls import ALL_WALLS, WallGrid


def test_new_grid_is_fully_closed() -> None:
    walls = WallGrid(4, 2)
    assert walls.to_lists() == [[ALL_WALLS] * 4] * 2


def test_open_north_opens_south_of_neighbour() -> None:
    walls = WallGrid(3, 3)
    walls.open_wall((1, 1), Direction.NORTH)
    assert not walls.has_wall((1, 1), Direction.NORTH)
    assert not walls.has_wall((1, 0), Direction.SOUTH)
    assert walls.check_coherence() == []


def test_open_east_opens_west_of_neighbour() -> None:
    # Non-square grid: swapping x and y would hit the wrong cell or go
    # out of range.
    walls = WallGrid(4, 2)
    walls.open_wall((2, 1), Direction.EAST)
    assert not walls.has_wall((2, 1), Direction.EAST)
    assert not walls.has_wall((3, 1), Direction.WEST)
    assert walls.to_lists()[0][2] == ALL_WALLS
    assert walls.check_coherence() == []


def test_open_west_opens_east_of_neighbour() -> None:
    walls = WallGrid(4, 2)
    walls.open_wall((1, 0), Direction.WEST)
    assert not walls.has_wall((1, 0), Direction.WEST)
    assert not walls.has_wall((0, 0), Direction.EAST)
    assert walls.to_lists()[1][1] == ALL_WALLS
    assert walls.check_coherence() == []


@pytest.mark.parametrize(
    ("cell", "direction"),
    [
        ((0, 0), Direction.NORTH),
        ((0, 0), Direction.WEST),
        ((3, 1), Direction.EAST),
        ((3, 1), Direction.SOUTH),
    ],
)
def test_open_border_raises(cell: tuple[int, int],
                            direction: Direction) -> None:
    walls = WallGrid(4, 2)
    with pytest.raises(ValueError):
        walls.open_wall(cell, direction)
    assert walls.to_lists() == WallGrid(4, 2).to_lists()


def test_to_lists_returns_a_copy() -> None:
    walls = WallGrid(2, 2)
    walls.to_lists()[0][0] = 0
    assert walls.has_wall((0, 0), Direction.NORTH)


def test_check_coherence_detects_one_sided_wall() -> None:
    walls = WallGrid(3, 3)
    # Break the invariant on purpose, bypassing open_wall.
    walls._cells[0][0] &= ~Direction.EAST
    errors = walls.check_coherence()
    assert len(errors) == 1
    assert "(0, 0) E" in errors[0]


def test_is_free() -> None:
    walls = WallGrid(4, 2)
    walls.block((2, 1))
    assert walls.is_free((0, 0))
    assert not walls.is_free((2, 1))
    assert not walls.is_free((4, 0))
    assert not walls.is_free((-1, 0))


@pytest.mark.parametrize(
    ("cell", "direction"),
    [
        ((1, 1), Direction.NORTH),  # from the blocked cell
        ((1, 0), Direction.SOUTH),  # into the blocked cell
        ((0, 1), Direction.EAST),
        ((2, 1), Direction.WEST),
    ],
)
def test_open_wall_of_blocked_cell_raises(cell: tuple[int, int],
                                          direction: Direction) -> None:
    walls = WallGrid(3, 3)
    walls.block((1, 1))
    with pytest.raises(ValueError):
        walls.open_wall(cell, direction)
    assert walls.to_lists() == WallGrid(3, 3).to_lists()


def test_block_outside_grid_raises() -> None:
    walls = WallGrid(3, 3)
    with pytest.raises(ValueError):
        walls.block((3, 0))


def test_block_after_carving_raises() -> None:
    walls = WallGrid(3, 3)
    walls.open_wall((0, 0), Direction.EAST)
    with pytest.raises(ValueError):
        walls.block((1, 0))

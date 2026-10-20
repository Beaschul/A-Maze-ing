"""Tests for perfect generation and the seed (#6).

Every algorithm in ALGORITHMS runs the same checks, so a new one (bonus)
is covered as soon as it is registered.
"""

from collections import deque

import pytest

from mazegen.algorithms import ALGORITHMS
from mazegen.directions import Direction
from mazegen.errors import MazeError
from mazegen.maze_generator import MazeGenerator
from mazegen.walls import ALL_WALLS, Cell, neighbour


def reachable(maze: MazeGenerator) -> set[Cell]:
    """Return the cells reachable from the entry through open walls."""
    seen = {maze.entry}
    queue = deque([maze.entry])
    while queue:
        cell = queue.popleft()
        for d in Direction:
            nxt = neighbour(cell, d)
            if not maze.has_wall(cell, d) and nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def free_cells(maze: MazeGenerator) -> set[Cell]:
    """Return every cell outside the "42" pattern."""
    every = {(x, y) for x in range(maze.width) for y in range(maze.height)}
    return every - maze.pattern_cells


def make(algorithm: str, seed: int = 42, width: int = 20,
         height: int = 15) -> MazeGenerator:
    """Build and generate a maze."""
    maze = MazeGenerator(width, height, (0, 0), (width - 1, height - 1),
                         seed=seed, algorithm=algorithm)
    maze.generate()
    return maze


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_same_seed_same_maze(algorithm: str) -> None:
    first, second = make(algorithm), make(algorithm)
    assert first.grid == second.grid
    assert first.carve_history == second.carve_history


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_different_seed_different_maze(algorithm: str) -> None:
    assert make(algorithm, seed=1).grid != make(algorithm, seed=2).grid


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_generate_twice_gives_same_maze(algorithm: str) -> None:
    maze = make(algorithm)
    grid = maze.grid
    maze.generate()
    assert maze.grid == grid


@pytest.mark.parametrize("algorithm", ALGORITHMS)
@pytest.mark.parametrize("size", [(20, 15), (5, 5), (2, 2), (9, 7)])
def test_every_free_cell_reachable(algorithm: str,
                                   size: tuple[int, int]) -> None:
    maze = make(algorithm, width=size[0], height=size[1])
    assert reachable(maze) == free_cells(maze)


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_maze_is_a_tree(algorithm: str) -> None:
    # A connected graph is a tree (no loop) iff edges == nodes - 1.
    maze = make(algorithm)
    assert len(maze.carve_history) == len(free_cells(maze)) - 1


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_pattern_cells_stay_closed(algorithm: str) -> None:
    maze = make(algorithm)
    assert maze.pattern_cells
    for x, y in maze.pattern_cells:
        assert maze.grid[y][x] == ALL_WALLS


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_big_maze_does_not_hit_recursion_limit(algorithm: str) -> None:
    maze = make(algorithm, width=100, height=100)
    assert reachable(maze) == free_cells(maze)


def test_seed_drawn_when_none() -> None:
    maze = MazeGenerator(20, 15, (0, 0), (19, 14))
    maze.generate()
    again = MazeGenerator(20, 15, (0, 0), (19, 14), seed=maze.seed)
    again.generate()
    assert again.grid == maze.grid


def test_unknown_algorithm_raises() -> None:
    with pytest.raises(MazeError, match="unknown algorithm"):
        MazeGenerator(20, 15, (0, 0), (19, 14), algorithm="nope")


def test_read_before_generate_raises() -> None:
    maze = MazeGenerator(20, 15, (0, 0), (19, 14))
    with pytest.raises(MazeError, match="generate"):
        maze.grid


def test_has_wall_outside_raises() -> None:
    maze = make("backtracker")
    with pytest.raises(MazeError, match="outside"):
        maze.has_wall((20, 0), Direction.NORTH)

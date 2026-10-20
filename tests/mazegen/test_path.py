"""Tests for the shortest path of generated mazes (#7).

The path is "replayed": starting at the entry, every letter is followed
through the maze, checking that the wall crossed is open. The length is
compared with a distance computed independently from the solver.
"""

from collections import deque

import pytest

from mazegen.algorithms import ALGORITHMS
from mazegen.directions import Direction
from mazegen.maze_generator import MazeGenerator
from mazegen.walls import Cell, neighbour

LETTERS = {"N": Direction.NORTH, "E": Direction.EAST,
           "S": Direction.SOUTH, "W": Direction.WEST}

SIZES = [(20, 15), (9, 7), (5, 5), (2, 2), (60, 40)]
SEEDS = [1, 2, 3, 42, 1337]


def make(algorithm: str, seed: int, width: int,
         height: int) -> MazeGenerator:
    """Build and generate a maze from the top-left to the bottom-right."""
    maze = MazeGenerator(width, height, (0, 0), (width - 1, height - 1),
                         seed=seed, algorithm=algorithm)
    maze.generate()
    return maze


def replay(maze: MazeGenerator) -> Cell:
    """Walk the solution letters from the entry and return the end cell.

    Fails the test as soon as a step crosses a closed wall.
    """
    cell = maze.entry
    for letter in maze.solution_directions:
        d = LETTERS[letter]
        assert not maze.has_wall(cell, d), f"closed {letter} wall at {cell}"
        cell = neighbour(cell, d)
    return cell


def distance(maze: MazeGenerator, start: Cell, goal: Cell) -> int:
    """Number of steps from ``start`` to ``goal``, without the solver."""
    steps = {start: 0}
    queue = deque([start])
    while queue:
        cell = queue.popleft()
        for d in Direction:
            nxt = neighbour(cell, d)
            if not maze.has_wall(cell, d) and nxt not in steps:
                steps[nxt] = steps[cell] + 1
                queue.append(nxt)
    return steps[goal]


@pytest.mark.parametrize("algorithm", ALGORITHMS)
@pytest.mark.parametrize("size", SIZES)
@pytest.mark.parametrize("seed", SEEDS)
def test_replay_only_crosses_open_walls_and_ends_at_exit(
        algorithm: str, size: tuple[int, int], seed: int) -> None:
    maze = make(algorithm, seed, *size)
    assert replay(maze) == maze.exit


@pytest.mark.parametrize("algorithm", ALGORITHMS)
@pytest.mark.parametrize("size", SIZES)
@pytest.mark.parametrize("seed", SEEDS)
def test_path_has_shortest_length(algorithm: str, size: tuple[int, int],
                                  seed: int) -> None:
    maze = make(algorithm, seed, *size)
    expected = distance(maze, maze.entry, maze.exit)
    assert len(maze.solution_directions) == expected


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_solution_cells_match_letters(algorithm: str) -> None:
    # Replaying the letters must visit exactly the cells of solution.
    maze = make(algorithm, 42, 20, 15)
    cells = [maze.entry]
    for letter in maze.solution_directions:
        cells.append(neighbour(cells[-1], LETTERS[letter]))
    assert cells == maze.solution


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_path_never_enters_the_pattern(algorithm: str) -> None:
    maze = make(algorithm, 42, 20, 15)
    assert not set(maze.solution) & maze.pattern_cells


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_path_never_visits_a_cell_twice(algorithm: str) -> None:
    maze = make(algorithm, 42, 60, 40)
    assert len(set(maze.solution)) == len(maze.solution)

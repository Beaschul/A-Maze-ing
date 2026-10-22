"""Checks on a carved maze: dead-ends, connectivity, loops, open areas.

Used by the tests and by the generator itself (the Pac-Man mode asks
:func:`creates_open_area` before opening each wall).

Only the free cells count: the "42" cells are treated like solid rock.

Every wall is shared by two cells (the EAST wall of a cell is the WEST wall
of the next one). To count each wall once, the functions only look at the
EAST and SOUTH walls of each cell.
"""

from collections import deque

from mazegen.directions import OPPOSITE, Direction
from mazegen.walls import Cell, WallGrid, neighbour

Wall = tuple[Cell, Direction]
"""A wall, named by one of its cells and the side it is on."""


def free_cells(grid: WallGrid) -> list[Cell]:
    """Return every cell outside the "42" pattern.

    Args:
        grid: Maze to inspect.

    Returns:
        The free cells, row by row.
    """
    return [
        (x, y)
        for y in range(grid.height)
        for x in range(grid.width)
        if grid.is_free((x, y))
    ]


def is_dead_end(grid: WallGrid, cell: Cell) -> bool:
    """Tell whether ``cell`` is free and has exactly 3 closed walls.

    Args:
        grid: Maze to inspect.
        cell: Position ``(x, y)`` inside the grid.

    Returns:
        True if the only way out of the cell is the way in.
    """
    closed = sum(grid.has_wall(cell, d) for d in Direction)
    return grid.is_free(cell) and closed == 3


def dead_ends(grid: WallGrid) -> list[Cell]:
    """Return every dead-end cell (see :func:`is_dead_end`).

    Args:
        grid: Maze to inspect.

    Returns:
        The dead-ends, row by row.
    """
    return [cell for cell in free_cells(grid) if is_dead_end(grid, cell)]


def count_components(grid: WallGrid) -> int:
    """Return how many separate regions the free cells form.

    Works like a paint bucket: each unpainted cell starts a new region,
    and the paint spreads through every open wall (breadth-first search).

    Args:
        grid: Maze to inspect.

    Returns:
        The number of regions (0 if there is no free cell).
    """
    seen: set[Cell] = set()
    components = 0
    for start in free_cells(grid):
        if start in seen:
            continue
        components += 1
        seen.add(start)
        queue: deque[Cell] = deque([start])
        while queue:
            cell = queue.popleft()
            for d in Direction:
                nxt = neighbour(cell, d)
                # The outer border is always closed, so nxt is inside.
                if not grid.has_wall(cell, d) and nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
    return components


def is_connected(grid: WallGrid) -> bool:
    """Tell whether every free cell can reach every other free cell.

    Args:
        grid: Maze to inspect.

    Returns:
        True if the free cells form a single region.
    """
    return count_components(grid) == 1


def count_passages(grid: WallGrid) -> int:
    """Return how many walls between two cells are open.

    Args:
        grid: Maze to inspect.

    Returns:
        The number of open walls, each shared wall counted once.
    """
    total = 0
    for cell in free_cells(grid):
        for d in (Direction.EAST, Direction.SOUTH):
            if not grid.has_wall(cell, d):
                total += 1
    return total


def loop_count(grid: WallGrid) -> int:
    """Return the number of independent loops (cyclomatic number).

    A region of N cells needs N - 1 passages to be connected without any
    loop (a perfect maze); every extra passage adds one loop. Hence::

        loops = passages - cells + regions

    Args:
        grid: Maze to inspect.

    Returns:
        0 for a perfect maze, more for a maze with alternative routes.
    """
    cells = len(free_cells(grid))
    return count_passages(grid) - cells + count_components(grid)


def _fits(grid: WallGrid, x0: int, y0: int, size: int) -> bool:
    """Tell whether a ``size`` x ``size`` window at ``(x0, y0)`` fits."""
    return (x0 >= 0 and y0 >= 0
            and x0 + size <= grid.width and y0 + size <= grid.height)


def _closed(grid: WallGrid, cell: Cell, d: Direction,
            pretend_open: Wall | None) -> bool:
    """Like ``grid.has_wall``, but the wall ``pretend_open`` is open."""
    if (cell, d) == pretend_open:
        return False
    return grid.has_wall(cell, d)


def _as_east_or_south(cell: Cell, d: Direction) -> Wall:
    """Name a wall from the cell on its west or north side.

    The WEST wall of ``(5, 3)`` is the EAST wall of ``(4, 3)``: this gives
    every wall a single name, the one :func:`window_is_open` looks for.
    """
    if d in (Direction.WEST, Direction.NORTH):
        return neighbour(cell, d), OPPOSITE[d]
    return cell, d


def window_is_open(grid: WallGrid, x0: int, y0: int, size: int,
                   pretend_open: Wall | None = None) -> bool:
    """Tell whether a ``size`` x ``size`` window has no wall inside it.

    Only the inner walls matter: the EAST walls of every column but the
    last one, and the SOUTH walls of every row but the last one. A window
    touching a "42" cell is never open, since those cells are fully closed.

    Args:
        grid: Maze to inspect.
        x0: Column of the top-left cell of the window.
        y0: Row of the top-left cell of the window.
        size: Side of the window, in cells.
        pretend_open: Wall ``(cell, EAST or SOUTH)`` to treat as open,
            to test a wall before opening it.

    Returns:
        True if the window fits in the grid and has no inner wall.
    """
    if not _fits(grid, x0, y0, size):
        return False
    last_x = x0 + size - 1
    last_y = y0 + size - 1
    for y in range(y0, y0 + size):
        for x in range(x0, x0 + size):
            cell = (x, y)
            if x < last_x and _closed(grid, cell, Direction.EAST,
                                      pretend_open):
                return False
            if y < last_y and _closed(grid, cell, Direction.SOUTH,
                                      pretend_open):
                return False
    return True


def has_open_3x3(grid: WallGrid) -> bool:
    """Tell whether any 3x3 block of the maze has no wall inside it.

    Args:
        grid: Maze to inspect.

    Returns:
        True if at least one open 3x3 area exists.
    """
    for y0 in range(grid.height):
        for x0 in range(grid.width):
            if window_is_open(grid, x0, y0, 3):
                return True
    return False


def creates_open_area(grid: WallGrid, cell: Cell, d: Direction,
                      size: int = 3) -> bool:
    """Tell whether opening wall ``d`` of ``cell`` would create an open area.

    The grid cannot close a wall again, so the wall is never opened here:
    it is only treated as open while the windows around it are checked.
    Only the windows containing ``cell`` are tested; the others did not
    change.

    Args:
        grid: Maze to inspect (left unchanged).
        cell: Position ``(x, y)`` of one side of the wall.
        d: Side of ``cell`` the wall is on.
        size: Side of the area: 3 for the forbidden 3x3 rooms, 2 to avoid
            small 2x2 rooms.

    Returns:
        True if, once the wall is open, a ``size`` x ``size`` window would
        have no wall inside it.
    """
    wall = _as_east_or_south(cell, d)
    x, y = wall[0]
    for y0 in range(y - size + 1, y + 1):
        for x0 in range(x - size + 1, x + 1):
            if window_is_open(grid, x0, y0, size, pretend_open=wall):
                return True
    return False

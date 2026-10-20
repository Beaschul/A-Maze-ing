"""Cells and the wall grid.

Coordinates are ``(x, y)``: ``x`` is the column (0 = left) and ``y`` is the
row (0 = top). Cells are stored row by row, so the masks are indexed
``[y][x]``.

Each cell stores its closed walls as a 4-bit mask, one bit per
:class:`~mazegen.directions.Direction`. Walls are only ever opened through
:meth:`WallGrid.open_wall`, which keeps both sides of a wall in agreement.
"""

from mazegen.directions import DELTA, LETTER, OPPOSITE, Direction

Cell = tuple[int, int]
"""A cell position ``(x, y)``."""

ALL_WALLS: int = 0xF
"""Wall mask of a fully closed cell."""


def neighbour(cell: Cell, d: Direction) -> Cell:
    """Return the cell next to ``cell`` in direction ``d``.

    Args:
        cell: Position ``(x, y)`` to start from.
        d: Direction to move in.

    Returns:
        The adjacent position. It may lie outside the grid.
    """
    x, y = cell
    dx, dy = DELTA[d]
    return x + dx, y + dy


class WallGrid:
    """Wall masks of a ``width`` x ``height`` maze, always coherent.

    Every cell starts fully closed. The masks are private: the only way to
    change them is :meth:`open_wall`, which updates both sides of a wall.

    Cells can be blocked with :meth:`block` (the "42" pattern): their walls
    can never be opened, so they stay fully closed. Algorithms pick their
    neighbours with :meth:`is_free` and treat blocked cells like cells
    outside the grid.

    Args:
        width: Number of columns.
        height: Number of rows.

    Attributes:
        width: Number of columns.
        height: Number of rows.
    """

    def __init__(self, width: int, height: int) -> None:
        """Create a ``width`` x ``height`` grid with every wall closed."""
        self.width: int = width
        self.height: int = height
        self._cells: list[list[int]] = [
            [ALL_WALLS] * width for _ in range(height)
        ]
        self._blocked: set[Cell] = set()

    def contains(self, cell: Cell) -> bool:
        """Tell whether ``cell`` lies inside the grid.

        Args:
            cell: Position ``(x, y)`` to test.

        Returns:
            True if the position is inside the grid, False otherwise.
        """
        x, y = cell
        return 0 <= x < self.width and 0 <= y < self.height

    def block(self, cell: Cell) -> None:
        """Block ``cell``: none of its walls can be opened from now on.

        Blocking must happen before carving, while the cell is still fully
        closed.

        Args:
            cell: Position ``(x, y)`` inside the grid.

        Raises:
            ValueError: If the cell is outside the grid or one of its walls
                is already open.
        """
        if not self.contains(cell):
            raise ValueError(f"cannot block {cell}: outside the grid")
        x, y = cell
        if self._cells[y][x] != ALL_WALLS:
            raise ValueError(f"cannot block {cell}: a wall is already open")
        self._blocked.add(cell)

    def is_free(self, cell: Cell) -> bool:
        """Tell whether ``cell`` is inside the grid and not blocked.

        Args:
            cell: Position ``(x, y)`` to test.

        Returns:
            True if an algorithm may carve into the cell, False otherwise.
        """
        return self.contains(cell) and cell not in self._blocked

    def has_wall(self, cell: Cell, d: Direction) -> bool:
        """Tell whether the wall on side ``d`` of ``cell`` is closed.

        Args:
            cell: Position ``(x, y)`` inside the grid.
            d: Side of the cell to look at.

        Returns:
            True if the wall is closed, False if it is open.
        """
        x, y = cell
        return bool(self._cells[y][x] & d)

    def open_wall(self, cell: Cell, d: Direction) -> None:
        """Open the wall on side ``d`` of ``cell`` and its neighbour's side.

        Args:
            cell: Position ``(x, y)`` inside the grid.
            d: Side of the wall to open.

        Raises:
            ValueError: If ``d`` points outside the grid (outer border), or
                ``cell`` or its neighbour is blocked.
        """
        other = neighbour(cell, d)
        if not self.contains(other):
            raise ValueError(
                f"cannot open {LETTER[d]} wall of {cell}: border")
        if cell in self._blocked or other in self._blocked:
            raise ValueError(
                f"cannot open {LETTER[d]} wall of {cell}: blocked cell")
        x, y = cell
        nx, ny = other
        self._cells[y][x] &= ~d
        self._cells[ny][nx] &= ~OPPOSITE[d]

    def check_coherence(self) -> list[str]:
        """Return a description of every wall inconsistency (empty if valid).

        Two neighbours share one wall, stored once in each cell. Both copies
        must agree: the east bit of a cell equals the west bit of the cell to
        its right, and the south bit equals the north bit of the cell below.

        Returns:
            One message per mismatched wall, for example
            ``"(0, 0) E != (1, 0) W"``. An empty list means the grid is
            coherent.
        """
        errors: list[str] = []
        for y in range(self.height):
            for x in range(self.width):
                cell = (x, y)
                # Checking only EAST and SOUTH visits every shared wall once:
                # the WEST/NORTH side is covered from the other cell.
                for d in (Direction.EAST, Direction.SOUTH):
                    other = neighbour(cell, d)
                    if not self.contains(other):
                        continue
                    mine = self.has_wall(cell, d)
                    theirs = self.has_wall(other, OPPOSITE[d])
                    if mine != theirs:
                        errors.append(f"{cell} {LETTER[d]} != "
                                      f"{other} {LETTER[OPPOSITE[d]]}")
        return errors

    def to_lists(self) -> list[list[int]]:
        """Return a copy of the wall masks.

        Returns:
            A new list of rows indexed ``[y][x]``. Changing it does not
            affect the grid.
        """
        return [row[:] for row in self._cells]

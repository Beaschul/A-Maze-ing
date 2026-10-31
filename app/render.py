"""Terminal ASCII rendering of a generated maze (subject, chapter V).

The drawing is a matrix of ``(2 * height + 1)`` rows by ``(2 * width + 1)``
columns::

    even row, even col  -> corner (always a wall)
    odd row,  odd col   -> cell (x, y) at (2y + 1, 2x + 1)
    odd row,  even col  -> vertical wall between two cells of a row
    even row, odd col   -> horizontal wall between two cells of a column

Every position is printed with two characters so the cells look square.
Layers are painted in order: walls, "42" pattern, path (if visible), then
entry and exit on top.

This module only reads the maze through the public ``MazeGenerator`` API:
it contains no generation logic.
"""

from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass
from enum import Enum
from itertools import groupby
from typing import Final

from mazegen import Cell, Direction, MazeGenerator


# ANSI escape sequences

RESET: Final[str] = "\033[0m"
"""Restore the default terminal colours."""

CLEAR_SCREEN: Final[str] = "\033[2J\033[H"
"""Clear the screen and move the cursor to the top-left corner."""

BLOCK: Final[str] = "██"
"""Two characters per position, so a cell is drawn as a square."""

EMPTY: Final[str] = "  "
"""An open position (cell or passage)."""


class Layer(Enum):
    """What is drawn at one position of the matrix."""

    OPEN = "open"
    WALL = "wall"
    PATTERN = "pattern"
    PATH = "path"
    ENTRY = "entry"
    EXIT = "exit"


@dataclass(frozen=True)
class Palette:
    """Colours of the walls and of the "42" pattern.

    Attributes:
        name: Name shown to the user.
        wall: ANSI SGR colour code of the walls (e.g. ``"97"``).
        pattern: ANSI SGR colour code of the "42" cells.
    """

    name: str
    wall: str
    pattern: str


PATH_COLOR: Final[str] = "93"
"""Bright yellow: the shortest path."""

ENTRY_COLOR: Final[str] = "92"
"""Bright green: the entry cell."""

EXIT_COLOR: Final[str] = "91"
"""Bright red: the exit cell."""

PALETTES: Final[tuple[Palette, ...]] = (
    Palette("white", wall="97", pattern="90"),
    Palette("cyan", wall="96", pattern="94"),
    Palette("magenta", wall="95", pattern="96"),
    Palette("blue", wall="94", pattern="95"),
)
"""Wall palettes to rotate through. None of them uses the path, entry or
exit colours, so those stay distinguishable whatever the palette."""


@dataclass
class RenderState:
    """Display options that the user can change while the program runs.

    Attributes:
        palette_index: Index of the current palette in :data:`PALETTES`.
        show_path: Whether the shortest path is drawn.
    """

    palette_index: int = 0
    show_path: bool = True

    @property
    def palette(self) -> Palette:
        """The palette currently in use."""
        return PALETTES[self.palette_index % len(PALETTES)]

    def next_palette(self) -> None:
        """Switch to the next wall palette, cycling back to the first."""
        self.palette_index = (self.palette_index + 1) % len(PALETTES)

    def toggle_path(self) -> None:
        """Show the path if it is hidden, hide it otherwise."""
        self.show_path = not self.show_path


def build_layers(maze: MazeGenerator, show_path: bool) -> list[list[Layer]]:
    """Compute what is drawn at each position of the matrix.

    Args:
        maze: A maze on which ``generate()`` was already called.
        show_path: Whether to include the shortest path.

    Returns:
        ``(2 * height + 1)`` rows of ``(2 * width + 1)`` layers.
    """
    grid = maze.grid
    rows = 2 * maze.height + 1
    cols = 2 * maze.width + 1
    layers = [[Layer.WALL] * cols for _ in range(rows)]

    for y, row in enumerate(grid):
        for x, mask in enumerate(row):
            layers[2 * y + 1][2 * x + 1] = Layer.OPEN
            # Each cell decides its east and south walls; the north and
            # west borders are drawn from the first row and column.
            if not mask & Direction.EAST:
                layers[2 * y + 1][2 * x + 2] = Layer.OPEN
            if not mask & Direction.SOUTH:
                layers[2 * y + 2][2 * x + 1] = Layer.OPEN
            if y == 0 and not mask & Direction.NORTH:
                layers[0][2 * x + 1] = Layer.OPEN
            if x == 0 and not mask & Direction.WEST:
                layers[2 * y + 1][0] = Layer.OPEN

    # The "42" cells, plus the walls and corners between them, so the
    # digits look solid instead of checkered.
    pattern = maze.pattern_cells
    for x, y in pattern:
        layers[2 * y + 1][2 * x + 1] = Layer.PATTERN
        if (x + 1, y) in pattern:
            layers[2 * y + 1][2 * x + 2] = Layer.PATTERN
        if (x, y + 1) in pattern:
            layers[2 * y + 2][2 * x + 1] = Layer.PATTERN
        if {(x + 1, y), (x, y + 1), (x + 1, y + 1)} <= pattern:
            layers[2 * y + 2][2 * x + 2] = Layer.PATTERN

    if show_path:
        path = maze.solution
        for (x1, y1), (x2, y2) in zip(path, path[1:]):
            # The passage between two cells sits halfway between them.
            layers[y1 + y2 + 1][x1 + x2 + 1] = Layer.PATH
        for x, y in path:
            layers[2 * y + 1][2 * x + 1] = Layer.PATH

    _set_cell(layers, maze.entry, Layer.ENTRY)
    _set_cell(layers, maze.exit, Layer.EXIT)
    return layers


def render(maze: MazeGenerator, state: RenderState) -> str:
    """Draw the maze with ANSI colours.

    Args:
        maze: A maze on which ``generate()`` was already called.
        state: Current display options.

    Returns:
        The drawing, one line per matrix row. Every line ends by resetting
        the colours, so the terminal is never left coloured.
    """
    colors = _colors(state.palette)
    lines = []
    for row in build_layers(maze, state.show_path):
        parts = []
        for layer, run in groupby(row):
            width = len(list(run))
            if layer is Layer.OPEN:
                parts.append(RESET + EMPTY * width)
            else:
                parts.append(f"\033[{colors[layer]}m" + BLOCK * width)
        lines.append("".join(parts) + RESET)
    return "\n".join(lines)


def fits_terminal(maze: MazeGenerator) -> bool:
    """Tell whether the drawing fits in the current terminal.

    Args:
        maze: The maze to draw.

    Returns:
        True if the terminal is wide and tall enough, False otherwise.
    """
    size = shutil.get_terminal_size()
    width = (2 * maze.width + 1) * len(BLOCK)
    height = 2 * maze.height + 1
    return width <= size.columns and height <= size.lines


def display(maze: MazeGenerator, state: RenderState) -> None:
    """Clear the screen and print the maze.

    A maze bigger than the terminal is still printed, after a warning.

    Args:
        maze: A maze on which ``generate()`` was already called.
        state: Current display options.
    """
    sys.stdout.write(CLEAR_SCREEN)
    if not fits_terminal(maze):
        print("Warning: the maze is bigger than the terminal, "
              "enlarge the window to see it correctly.")
    print(render(maze, state))
    print(legend(state))


def legend(state: RenderState) -> str:
    """Return a one-line coloured legend of the drawing.

    Args:
        state: Current display options.

    Returns:
        The legend, ending with a colour reset.
    """
    colors = _colors(state.palette)
    items = [
        (Layer.ENTRY, "entry"),
        (Layer.EXIT, "exit"),
        (Layer.PATH, "path" if state.show_path else "path (hidden)"),
        (Layer.PATTERN, "42"),
        (Layer.WALL, f"walls ({state.palette.name})"),
    ]
    return "  ".join(
        f"\033[{colors[layer]}m{BLOCK}{RESET} {label}"
        for layer, label in items
    )


def _colors(palette: Palette) -> dict[Layer, str]:
    """Map every drawn layer to its ANSI colour code."""
    return {
        Layer.WALL: palette.wall,
        Layer.PATTERN: palette.pattern,
        Layer.PATH: PATH_COLOR,
        Layer.ENTRY: ENTRY_COLOR,
        Layer.EXIT: EXIT_COLOR,
    }


def _set_cell(layers: list[list[Layer]], cell: Cell, layer: Layer) -> None:
    """Paint the matrix position of ``cell`` with ``layer``."""
    x, y = cell
    layers[2 * y + 1][2 * x + 1] = layer

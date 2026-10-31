"""Interactive menu shown under the maze (subject, chapter V).

The loop is: draw the maze, print the menu, read one choice, act on it.
Everything the menu can change lives in :class:`MenuState`.

Choices:
    1. Re-generate: builds a new maze with a new random seed and REWRITES
       the output file, so the file always matches what is on screen.
    2. Show/Hide the shortest path.
    3. Change the colours of the walls (and of the "42" pattern).
    4. Quit.

Invalid input only prints a message and asks again. Ctrl+D (``EOFError``)
and Ctrl+C (``KeyboardInterrupt``) quit the menu cleanly.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Final

from app.config import MazeConfig
from app.render import RenderState, display
from mazegen import MazeGenerator
from mazegen.errors import MazeError
from mazegen.writer import write_output


TOO_SMALL_FOR_42: Final[str] = (
    "Error: the maze is too small to draw the \"42\" pattern."
)
"""The subject allows omitting the "42", but requires an error message."""


class Action(Enum):
    """What the user can ask the menu to do."""

    REGENERATE = "1"
    TOGGLE_PATH = "2"
    NEXT_COLORS = "3"
    QUIT = "4"


MENU_LABELS: Final[dict[Action, str]] = {
    Action.REGENERATE: "Re-generate a new maze",
    Action.TOGGLE_PATH: "Show/Hide the shortest path",
    Action.NEXT_COLORS: "Change wall colours",
    Action.QUIT: "Quit",
}
"""Text of each menu entry, in display order."""


@dataclass
class MenuState:
    """Everything the menu can change while the program runs.

    Attributes:
        config: The parsed configuration (size, entry, exit, output file).
        maze: The maze currently on screen (already generated).
        view: Display options (path visibility, palette).
        message: Feedback of the last action, shown above the menu.
        running: False once the user asked to quit.
    """

    config: MazeConfig
    maze: MazeGenerator
    view: RenderState = field(default_factory=RenderState)
    message: str = ""
    running: bool = True


def build_maze(config: MazeConfig, seed: int | None) -> MazeGenerator:
    """Create and generate a maze from the configuration.

    Args:
        config: The parsed configuration.
        seed: Seed of the maze. None draws a random one (kept in
            ``maze.seed``).

    Returns:
        A generated maze.

    Raises:
        MazeError: If no valid maze exists for these parameters.
    """
    maze = MazeGenerator(
        width=config.width,
        height=config.height,
        entry=config.entry,
        exit=config.exit,
        perfect=config.perfect,
        seed=seed,
    )
    maze.generate()
    return maze


def save_maze(maze: MazeGenerator, path: str) -> None:
    """Write ``maze`` to ``path`` in the output format of the subject.

    Each cell is a wall bitmask (N=1, E=2, S=4, W=8), which is the encoding
    the subject expects, so one hex digit per cell suffices.

    Args:
        maze: A generated maze.
        path: Destination file.

    Raises:
        OSError: If the file cannot be written.
    """
    write_output(
        path=path,
        hex_rows=["".join(f"{cell:x}" for cell in row) for row in maze.grid],
        entry=maze.entry,
        exit=maze.exit,
        path_moves=maze.solution_directions,
    )


def parse_choice(text: str) -> Action | None:
    """Turn what the user typed into an action.

    Args:
        text: Raw input line.

    Returns:
        The matching action, or None if the input is not a valid choice.
    """
    choice = text.strip()
    for action in Action:
        if action.value == choice:
            return action
    return None


def menu_text(state: MenuState) -> str:
    """Return the menu printed under the maze.

    Args:
        state: Current menu state.

    Returns:
        The status line (seed, size, path length), the last message if any,
        and the numbered choices.
    """
    maze = state.maze
    lines = [
        f"Seed: {maze.seed}  |  {maze.width}x{maze.height}  |  "
        f"{'perfect' if maze.perfect else 'Pac-Man'}  |  "
        f"shortest path: {len(maze.solution_directions)} steps  |  "
        f"file: {state.config.output_file}",
    ]
    if state.message:
        lines.append(state.message)
    lines.append("=== A-Maze-ing ===")
    lines.extend(
        f"{action.value}. {label}" for action, label in MENU_LABELS.items()
    )
    return "\n".join(lines)


def regenerate(state: MenuState) -> None:
    """Replace the maze by a new one with a random seed and save it.

    The output file is rewritten so it always matches the maze on screen.
    On error the current maze is kept and the error becomes the message.

    Args:
        state: Current menu state, updated in place.
    """
    try:
        maze = build_maze(state.config, seed=None)
    except MazeError as exc:
        state.message = f"MazeError: {exc}"
        return
    try:
        save_maze(maze, state.config.output_file)
    except OSError as exc:
        state.message = f"WriteError: {exc} (new maze not saved)"
    else:
        state.message = (
            f"New maze generated (seed {maze.seed}), "
            f"saved to {state.config.output_file}."
        )
    state.maze = maze
    if not maze.pattern_cells:
        state.message += "\n" + TOO_SMALL_FOR_42


def apply(state: MenuState, action: Action) -> None:
    """Run one menu action.

    Args:
        state: Current menu state, updated in place.
        action: The action chosen by the user.
    """
    if action is Action.REGENERATE:
        regenerate(state)
    elif action is Action.TOGGLE_PATH:
        state.view.toggle_path()
        state.message = (
            "Path shown." if state.view.show_path else "Path hidden."
        )
    elif action is Action.NEXT_COLORS:
        state.view.next_palette()
        state.message = f"Colours: {state.view.palette.name}."
    else:
        state.running = False


def run_menu(
    state: MenuState,
    read: Callable[[str], str] | None = None,
    show: Callable[[MazeGenerator, RenderState], None] = display,
) -> None:
    """Draw the maze and handle the user's choices until they quit.

    Args:
        state: Initial menu state.
        read: Function reading one line of input. None uses the builtin
            ``input``, looked up at call time.
        show: Function drawing the maze (``display`` by default).
    """
    if read is None:
        read = input
    while state.running:
        try:
            show(state.maze, state.view)
            print(menu_text(state))
            text = read("Your choice: ")
            action = parse_choice(text)
            if action is None:
                state.message = (
                    f"Invalid choice {text.strip()!r}: "
                    f"type a number from 1 to {len(Action)}."
                )
                continue
            state.message = ""
            apply(state, action)
        except (EOFError, KeyboardInterrupt):
            # Ctrl+D / Ctrl+C: quit like choice 4, without a traceback.
            print()
            state.running = False

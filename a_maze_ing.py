"""A-Maze-ing — entry point."""

from __future__ import annotations

import sys

from app.config import parse_config
from app.errors import ConfigError
from app.menu import TOO_SMALL_FOR_42, MenuState, build_maze, run_menu, \
    save_maze
from mazegen.errors import MazeError


def main(argv: list[str]) -> int:
    """Run the maze generator, then the interactive menu.

    Args:
        argv: Command-line arguments (excluding the program name).

    Returns:
        Process exit code (0 on success, 1 on error).
    """
    if len(argv) != 1:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 1

    # 1. Parse and validate the config file
    try:
        config = parse_config(argv[0])
    except ConfigError as exc:
        print(f"ConfigError: {exc}", file=sys.stderr)
        return 1

    # 2. Generate the maze
    try:
        maze = build_maze(config, seed=config.seed)
    except MazeError as exc:
        print(f"MazeError: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 — safety net
        print(f"Unexpected generation error: {exc}", file=sys.stderr)
        return 1

    # 3. Write the output file
    try:
        save_maze(maze, config.output_file)
    except OSError as exc:
        print(f"WriteError: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Unexpected write error: {exc}", file=sys.stderr)
        return 1

    # 4. Display the maze and let the user interact with it
    state = MenuState(
        config=config,
        maze=maze,
        message=f"OK: maze written to {config.output_file}.",
    )
    # The subject allows omitting the "42" when the maze is too small,
    # but requires an error message on the console in that case.
    if not maze.pattern_cells:
        state.message += "\n" + TOO_SMALL_FOR_42
    try:
        run_menu(state)
    except Exception as exc:  # noqa: BLE001
        print(f"Unexpected display error: {exc}", file=sys.stderr)
        return 1

    print("Bye!")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        print("\nInterrupted by user.", file=sys.stderr)
        sys.exit(130)

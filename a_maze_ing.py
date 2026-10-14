from __future__ import annotations

import sys

from mazegen.config import parse_config
from mazegen.errors import ConfigError


def main(argv: list[str]) -> int:
    """Run the maze generator.

    Args:
        argv: Command-line arguments (excluding the program name).

    Returns:
        Process exit code (0 on success, 1 on error).
    """
    if len(argv) != 1:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 1

    try:
        config = parse_config(argv[0])
    except ConfigError as exc:
        print(f"ConfigError: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 — last-resort safety net
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1

    print(f"OK: {config}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
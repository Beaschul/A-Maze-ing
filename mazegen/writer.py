"""File writer for the A-Maze-ing output format.

The output format is described in section IV.5 of the subject:

    <hex row 0>
    ...
    <hex row N-1>
    <empty line>
    <entry_x>,<entry_y>
    <exit_x>,<exit_y>
    <path>

Every line ends with ``\n``, including the last one.
"""

from __future__ import annotations

from pathlib import Path


def write_output(
    path: str | Path,
    *,
    hex_rows: list[str],
    entry: tuple[int, int],
    exit: tuple[int, int],
    path_moves: str,
) -> None:
    """Write the maze to a file in the IV.5 output format.

    Args:
        path: Destination file path.
        hex_rows: One hexadecimal string per grid row.
        entry: ``(x, y)`` entry coordinates.
        exit: ``(x, y)`` exit coordinates.
        path_moves: Shortest path as a string of ``N``/``E``/``S``/``W``.

    Raises:
        OSError: If the file cannot be written (missing directory,
            permission denied, disk full, etc.).
    """
    lines: list[str] = []

    # 1. Grid: one hex line per row
    lines.extend(hex_rows)

    # 2. Empty separator line
    lines.append("")

    # 3. Entry and exit coordinates
    lines.append(f"{entry[0]},{entry[1]}")
    lines.append(f"{exit[0]},{exit[1]}")

    # 4. Shortest path
    lines.append(path_moves)

    # Join with \n and force a final newline on the last line
    content = "\n".join(lines) + "\n"

    # Write with explicit UTF-8 and NO newline translation
    # (newline="" prevents Python from turning \n into \r\n on Windows)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(content)

"""Run a_maze_ing + maze_analyzer over every test config and many seeds.

For each file in ``tests/configs_valid/`` and each seed, the program is run
with ``SEED`` and ``OUTPUT_FILE`` overridden, then the output is checked:

* the analyzer verdict must be ``PERFECT maze`` (``PERFECT=True``) or
  ``Pac-Man-USABLE`` (``PERFECT=False``);
* the footer path must start at the entry, cross no wall, end at the exit
  and be a shortest path (the analyzer does not check this);
* the "42" pattern must be drawn when the maze is big enough, and only then.

A config whose first lines contain ``# EXPECT_ERROR: <text>`` must instead
make the program fail with an error message containing ``<text>``.

Usage::

    python3 tools/run_analyzer.py [--seeds N] [config ...]

Only the failures are detailed; the exit code is 1 if anything failed.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import sys
import tempfile
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import a_maze_ing  # noqa: E402
import maze_analyzer as ma  # noqa: E402
from mazegen.constants import (  # noqa: E402
    PATTERN_42,
    PATTERN_MIN_HEIGHT,
    PATTERN_MIN_WIDTH,
)

CONFIG_DIR = ROOT / "tests" / "configs_valid"
DEFAULT_SEEDS = 50
EXPECT_ERROR = "# EXPECT_ERROR:"
PATTERN_CELLS = sum(row.count("#") for row in PATTERN_42)
OVERRIDDEN_KEYS = ("SEED=", "OUTPUT_FILE=")

# Move letter -> (dx, dy, wall bit)
MOVES: dict[str, tuple[int, int, int]] = {
    "N": (0, -1, 1),
    "E": (1, 0, 2),
    "S": (0, 1, 4),
    "W": (-1, 0, 8),
}


def read_config(path: Path) -> tuple[list[str], dict[str, str], str | None]:
    """Return the config lines (minus overridden keys), its values, and the
    expected error text if any."""
    lines: list[str] = []
    values: dict[str, str] = {}
    expected: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(EXPECT_ERROR):
            expected = line[len(EXPECT_ERROR):].strip()
            continue
        if line.startswith(OVERRIDDEN_KEYS):
            continue
        lines.append(line)
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            values[key] = value
    return lines, values, expected


def run_program(config: Path) -> tuple[int, str]:
    """Run a_maze_ing in-process; return its exit code and output."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), \
            contextlib.redirect_stderr(buffer):
        code = a_maze_ing.main([str(config)])
    return code, buffer.getvalue()


def check_path(maze: ma.Maze, path: str) -> str | None:
    """Walk the footer path; return a problem description, or None."""
    if maze.entry is None or maze.exit is None:
        return "footer has no valid entry/exit"
    row, col = maze.entry
    for index, move in enumerate(path):
        if move not in MOVES:
            return f"path has invalid move {move!r} at step {index}"
        dx, dy, bit = MOVES[move]
        if maze.grid[row][col] & bit:
            return f"path crosses a wall at step {index} ({col},{row}) {move}"
        row, col = row + dy, col + dx
        if (row, col) not in maze:
            return f"path leaves the grid at step {index}"
    if (row, col) != maze.exit:
        return f"path ends at ({col},{row}), not at the exit"
    distance = {maze.entry: 0}
    queue = deque([maze.entry])
    while queue:
        cell = queue.popleft()
        for nxt in maze.passages(cell):
            if nxt not in distance:
                distance[nxt] = distance[cell] + 1
                queue.append(nxt)
    if distance.get(maze.exit) != len(path):
        return (f"path has {len(path)} steps, shortest is "
                f"{distance.get(maze.exit)}")
    return None


def check_output(output: Path, values: dict[str, str]) -> list[str]:
    """Analyze one generated maze; return the list of problems."""
    problems: list[str] = []
    try:
        maze = ma.Maze.from_file(str(output))
    except ma.MazeError as error:
        return [f"malformed output: {error}"]
    report = ma.analyze(maze)
    verdict = ma.verdict(
        report, ma.DEFAULT_MIN_LOOPS, ma.DEFAULT_MAX_DEAD_ENDS
    )
    perfect = values["PERFECT"] == "True"
    wanted = "PERFECT maze" if perfect else "Pac-Man-USABLE"
    if not verdict.startswith(wanted):
        problems.append(verdict)
    lines = output.read_text(encoding="utf-8").rstrip("\n").split("\n")
    path_problem = check_path(maze, lines[-1])
    if path_problem:
        problems.append(path_problem)
    fits = (int(values["WIDTH"]) >= PATTERN_MIN_WIDTH
            and int(values["HEIGHT"]) >= PATTERN_MIN_HEIGHT)
    closed = sum(1 for cell in maze if maze.is_fully_closed(cell))
    if fits and closed != PATTERN_CELLS:
        problems.append(f'"42" has {closed} closed cells, '
                        f"expected {PATTERN_CELLS}")
    if not fits and closed:
        problems.append(f'{closed} closed cells but "42" does not fit')
    return problems


def run_config(path: Path, seeds: int, workdir: Path) -> list[str]:
    """Run one config over every seed; return the failure messages."""
    lines, values, expected = read_config(path)
    config = workdir / "config.txt"
    output = workdir / "maze.txt"
    failures: list[str] = []
    for seed in range(1, seeds + 1):
        config.write_text(
            "\n".join(lines + [f"SEED={seed}", f"OUTPUT_FILE={output}"])
            + "\n",
            encoding="utf-8",
        )
        code, text = run_program(config)
        if expected is not None:
            if code == 0 or expected not in text:
                failures.append(f"seed {seed}: expected error containing "
                                f"{expected!r}, got: {text.strip()}")
            continue
        if code != 0:
            failures.append(f"seed {seed}: program failed: {text.strip()}")
            continue
        failures += [f"seed {seed}: {problem}"
                     for problem in check_output(output, values)]
    return failures


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seeds", type=int, default=DEFAULT_SEEDS,
                        metavar="N", help="seeds 1..N per config "
                        "(default: %(default)s)")
    parser.add_argument("configs", nargs="*", type=Path,
                        help=f"configs to run (default: {CONFIG_DIR.name}/)")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    configs = args.configs or sorted(CONFIG_DIR.glob("*.txt"))
    failed: dict[str, list[str]] = {}
    with tempfile.TemporaryDirectory() as tmp:
        for path in configs:
            failures = run_config(path, args.seeds, Path(tmp))
            status = "FAIL" if failures else "ok"
            print(f"{status:4}  {path.name}")
            if failures:
                failed[path.name] = failures
    print(f"\n{len(configs) - len(failed)}/{len(configs)} configs passed "
          f"({args.seeds} seeds each)")
    for name, failures in failed.items():
        print(f"\n{name}: {len(failures)} failure(s)")
        for failure in failures[:5]:
            print(f"  - {failure}")
        if len(failures) > 5:
            print(f"  ... (+{len(failures) - 5} more)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

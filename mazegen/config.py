from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Final

from mazegen.errors import ConfigError


MAX_DIMENSION: Final[int] = 500
"""Upper bound for WIDTH/HEIGHT to avoid absurd allocations."""

MIN_DIMENSION: Final[int] = 2
"""Minimum WIDTH/HEIGHT (a maze needs at least 2x2)."""

MANDATORY_KEYS: Final[frozenset[str]] = frozenset({
    "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT",
})

OPTIONAL_KEYS: Final[frozenset[str]] = frozenset({
    "SEED",
})

KNOWN_KEYS: Final[frozenset[str]] = MANDATORY_KEYS | OPTIONAL_KEYS


@dataclass(frozen=True)
class MazeConfig:
    """Validated configuration for maze generation.

    Attributes:
        width: Number of cells horizontally.
        height: Number of cells vertically.
        entry: (x, y) entry coordinates.
        exit: (x, y) exit coordinates.
        output_file: Path where the maze will be written.
        perfect: Whether to generate a perfect maze.
        seed: Optional RNG seed for reproducibility.
    """

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None


def parse_config(path: str) -> MazeConfig:
    """Read and validate a configuration file.

    Args:
        path: Path to the configuration file.

    Returns:
        A fully validated MazeConfig.

    Raises:
        ConfigError: If the file cannot be read, has invalid syntax,
            is missing mandatory keys, or contains out-of-range values.
    """
    raw = _read_lines(path)
    return _build_config(raw, config_path=path)


def _read_lines(path: str) -> list[tuple[int, str]]:
    """Return (line_number, stripped_line) for meaningful lines.

    Args:
        path: Path to the configuration file.

    Returns:
        List of (1-based line number, stripped content) tuples, skipping
        blank lines and full-line comments.

    Raises:
        ConfigError: On any file-related error or encoding problem.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()
    except FileNotFoundError as exc:
        raise ConfigError(f"configuration file not found: {path!r}") from exc
    except IsADirectoryError as exc:
        raise ConfigError(f"{path!r} is a directory, not a file") from exc
    except PermissionError as exc:
        raise ConfigError(f"permission denied reading {path!r}") from exc
    except UnicodeDecodeError as exc:
        raise ConfigError(
            f"{path!r} is not valid UTF-8 (byte {exc.start})"
        ) from exc
    except OSError as exc:
        raise ConfigError(f"cannot read {path!r}: {exc}") from exc

    result: list[tuple[int, str]] = []
    for i, line in enumerate(raw_lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        result.append((i, stripped))
    return result


def _build_config(
    raw: list[tuple[int, str]], config_path: str
) -> MazeConfig:
    """Turn raw (line_no, text) pairs into a validated MazeConfig."""
    values: dict[str, tuple[int, str]] = {}

    for line_no, text in raw:
        if "=" not in text:
            raise ConfigError(
                f"missing '=' in line: {text!r}", line=line_no
            )
        key, _, value = text.partition("=")
        key = key.strip()
        value = value.strip()

        if not key:
            raise ConfigError("empty key before '='", line=line_no)
        if key not in KNOWN_KEYS:
            print(f"warning: unknown key {key!r} (line {line_no})")
            continue
        if key in values:
            raise ConfigError(
                f"duplicate key {key!r} "
                f"(first seen on line {values[key][0]})",
                line=line_no,
            )
        values[key] = (line_no, value)

    _check_mandatory(values)

    width = _parse_int(values, "WIDTH")
    height = _parse_int(values, "HEIGHT")

    if width < MIN_DIMENSION or height < MIN_DIMENSION:
        raise ConfigError(
            f"WIDTH and HEIGHT must be >= {MIN_DIMENSION}",
            line=values["WIDTH"][0] if width < MIN_DIMENSION else values["HEIGHT"][0],
        )
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ConfigError(
            f"WIDTH and HEIGHT must be <= {MAX_DIMENSION}",
            line=values["WIDTH"][0] if width > MAX_DIMENSION else values["HEIGHT"][0],
        )

    entry = _parse_coord(values, "ENTRY", width, height)
    exit_ = _parse_coord(values, "EXIT", width, height)

    if entry == exit_:
        raise ConfigError(
            "ENTRY and EXIT must be different cells",
            line=values["EXIT"][0],
        )

    output_file = values["OUTPUT_FILE"][1]
    if not output_file:
        raise ConfigError(
            "OUTPUT_FILE cannot be empty", line=values["OUTPUT_FILE"][0]
        )
    if os.path.abspath(output_file) == os.path.abspath(config_path):
        raise ConfigError(
            "OUTPUT_FILE cannot be the configuration file itself",
            line=values["OUTPUT_FILE"][0],
        )

    perfect = _parse_bool(values, "PERFECT")
    seed = _parse_optional_int(values, "SEED")

    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit=exit_,
        output_file=output_file,
        perfect=perfect,
        seed=seed,
    )


def _check_mandatory(values: dict[str, tuple[int, str]]) -> None:
    missing = MANDATORY_KEYS - values.keys()
    if missing:
        pretty = ", ".join(sorted(missing))
        raise ConfigError(f"missing mandatory key(s): {pretty}")


def _parse_int(values: dict[str, tuple[int, str]], key: str) -> int:
    line_no, raw = values[key]
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigError(
            f"{key} must be an integer, got {raw!r}", line=line_no
        ) from exc


def _parse_optional_int(
    values: dict[str, tuple[int, str]], key: str
) -> int | None:
    if key not in values:
        return None
    return _parse_int(values, key)


def _parse_bool(values: dict[str, tuple[int, str]], key: str) -> bool:
    line_no, raw = values[key]
    lowered = raw.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise ConfigError(
        f"{key} must be True or False, got {raw!r}", line=line_no
    )


def _parse_coord(
    values: dict[str, tuple[int, str]],
    key: str,
    width: int,
    height: int,
) -> tuple[int, int]:
    line_no, raw = values[key]
    parts = raw.split(",")
    if len(parts) != 2:
        raise ConfigError(
            f"{key} must be in 'x,y' format, got {raw!r}", line=line_no
        )
    try:
        x = int(parts[0].strip())
        y = int(parts[1].strip())
    except ValueError as exc:
        raise ConfigError(
            f"{key} coordinates must be integers, got {raw!r}", line=line_no
        ) from exc
    if not (0 <= x < width and 0 <= y < height):
        raise ConfigError(
            f"{key}=({x},{y}) is outside the {width}x{height} grid",
            line=line_no,
        )
    return (x, y)

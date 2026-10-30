"""Tests for the output file writer (format of section IV.5)."""

from pathlib import Path

import pytest

from mazegen.writer import write_output


def write(path: Path, path_moves: str = "ES") -> bytes:
    """Write the README 3x2 maze to *path* and return the raw bytes."""
    write_output(
        path,
        hex_rows=["9d3", "ac6"],
        entry=(0, 0),
        exit=(2, 0),
        path_moves=path_moves,
    )
    return path.read_bytes()


def test_writes_grid_blank_line_entry_exit_and_path(tmp_path: Path) -> None:
    content = write(tmp_path / "maze.txt").decode("utf-8")
    assert content == "9d3\nac6\n\n0,0\n2,0\nES\n"


def test_last_line_ends_with_newline(tmp_path: Path) -> None:
    assert write(tmp_path / "maze.txt").endswith(b"ES\n")


def test_uses_lf_only(tmp_path: Path) -> None:
    assert b"\r" not in write(tmp_path / "maze.txt")


def test_coordinates_are_x_then_y(tmp_path: Path) -> None:
    out = tmp_path / "maze.txt"
    write_output(out, hex_rows=["f"], entry=(3, 7), exit=(5, 1),
                 path_moves="")
    lines = out.read_text(encoding="utf-8").split("\n")
    assert lines[2:4] == ["3,7", "5,1"]


def test_empty_path_still_writes_its_line(tmp_path: Path) -> None:
    content = write(tmp_path / "maze.txt", path_moves="").decode("utf-8")
    assert content == "9d3\nac6\n\n0,0\n2,0\n\n"


def test_accepts_str_path(tmp_path: Path) -> None:
    out = tmp_path / "maze.txt"
    write_output(str(out), hex_rows=["9d3"], entry=(0, 0), exit=(2, 0),
                 path_moves="EE")
    assert out.read_text(encoding="utf-8") == "9d3\n\n0,0\n2,0\nEE\n"


def test_overwrites_existing_file(tmp_path: Path) -> None:
    out = tmp_path / "maze.txt"
    out.write_text("old content that is longer than the new one\n" * 10)
    assert write(out) == b"9d3\nac6\n\n0,0\n2,0\nES\n"


def test_missing_directory_raises_oserror(tmp_path: Path) -> None:
    with pytest.raises(OSError):
        write(tmp_path / "missing" / "maze.txt")


def test_directory_as_path_raises_oserror(tmp_path: Path) -> None:
    with pytest.raises(OSError):
        write_output(tmp_path, hex_rows=["f"], entry=(0, 0), exit=(0, 0),
                     path_moves="")

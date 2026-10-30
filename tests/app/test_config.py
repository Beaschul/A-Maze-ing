"""Tests for the configuration parser.

Every file in ``tests/configs_invalid/`` holds exactly one error. Each one
must raise ``ConfigError`` with a clear message, and the program must exit
with code 1 without a traceback.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from a_maze_ing import main
from app.config import MAX_SHOWN_VALUE, MazeConfig, parse_config
from app.errors import ConfigError

ROOT: Path = Path(__file__).resolve().parents[2]
INVALID_DIR: Path = ROOT / "tests" / "configs_invalid"

VALID: str = (
    "WIDTH=20\n"
    "HEIGHT=15\n"
    "ENTRY=0,0\n"
    "EXIT=19,14\n"
    "OUTPUT_FILE=maze.txt\n"
    "PERFECT=True\n"
)

# File name -> a piece of the message the user must see.
EXPECTED: dict[str, str] = {
    "empty_file": "missing mandatory key(s)",
    "only_comments": "missing mandatory key(s)",
    "missing_equals": "line 8: missing '='",
    "empty_key": "line 8: empty key",
    "duplicate_key": "line 8: duplicate key 'WIDTH'",
    "missing_width": "missing mandatory key(s): WIDTH",
    "missing_height": "missing mandatory key(s): HEIGHT",
    "missing_entry": "missing mandatory key(s): ENTRY",
    "missing_exit": "missing mandatory key(s): EXIT",
    "missing_output_file": "missing mandatory key(s): OUTPUT_FILE",
    "missing_perfect": "missing mandatory key(s): PERFECT",
    "lowercase_key": "missing mandatory key(s): WIDTH",
    "width_not_integer": "line 2: WIDTH must be an integer",
    "width_float": "line 2: WIDTH must be an integer",
    "width_empty": "line 2: WIDTH must be an integer",
    "width_zero": "line 2: WIDTH and HEIGHT must be >= 2",
    "width_negative": "line 2: WIDTH and HEIGHT must be >= 2",
    "width_too_small": "line 2: WIDTH and HEIGHT must be >= 2",
    "width_too_big": "line 2: WIDTH and HEIGHT must be <= 500",
    "width_huge_number": "line 2: WIDTH must be an integer",
    "height_not_integer": "line 3: HEIGHT must be an integer",
    "height_too_big": "line 3: WIDTH and HEIGHT must be <= 500",
    "entry_bad_separator": "line 4: ENTRY must be in 'x,y' format",
    "entry_three_values": "line 4: ENTRY must be in 'x,y' format",
    "entry_not_integer": "line 4: ENTRY coordinates must be integers",
    "entry_outside_grid": "line 4: ENTRY=(20,0) is outside",
    "entry_negative": "line 4: ENTRY=(-1,0) is outside",
    "exit_outside_grid": "line 5: EXIT=(19,15) is outside",
    "exit_empty": "line 5: EXIT must be in 'x,y' format",
    "entry_equals_exit": "line 5: ENTRY and EXIT must be different",
    "perfect_invalid": "line 7: PERFECT must be True or False",
    "perfect_number": "line 7: PERFECT must be True or False",
    "output_file_empty": "line 6: OUTPUT_FILE cannot be empty",
    "output_file_is_config": "line 6: OUTPUT_FILE cannot be the config",
    "seed_not_integer": "line 8: SEED must be an integer",
    "not_utf8": "is not valid UTF-8",
}


def write_config(folder: Path, text: str, name: str = "config.txt") -> str:
    """Write a configuration file and return its path.

    Args:
        folder: Directory where the file is created.
        text: Content of the file.
        name: File name.

    Returns:
        The path of the new file, as a string.
    """
    path = folder / name
    path.write_text(text, encoding="utf-8")
    return str(path)


def can_read(path: Path) -> bool:
    """Tell whether the current user can still open ``path``.

    Args:
        path: File to try.

    Returns:
        True if the file could be opened.
    """
    try:
        with open(path, "rb"):
            return True
    except PermissionError:
        return False


def test_every_invalid_file_has_an_expected_message() -> None:
    """Each file in the folder is listed in EXPECTED, and vice versa."""
    files = {path.stem for path in INVALID_DIR.glob("*.txt")}
    assert files == set(EXPECTED)


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_invalid_config_raises_clear_error(
    name: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The parser rejects the file with the expected message."""
    # OUTPUT_FILE paths in the files are relative to their own folder.
    monkeypatch.chdir(INVALID_DIR)
    with pytest.raises(ConfigError) as info:
        parse_config(f"{name}.txt")
    assert EXPECTED[name] in str(info.value)


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_invalid_config_never_crashes(
    name: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The program prints the error and exits with 1, with no traceback."""
    monkeypatch.chdir(INVALID_DIR)
    assert main([f"{name}.txt"]) == 1
    err = capsys.readouterr().err
    assert "ConfigError: " in err
    assert "Traceback" not in err


def test_missing_file(tmp_path: Path) -> None:
    """A file that does not exist gives a clear error."""
    with pytest.raises(ConfigError, match="not found"):
        parse_config(str(tmp_path / "nope.txt"))


def test_directory_instead_of_file(tmp_path: Path) -> None:
    """A directory is not accepted as a configuration file."""
    with pytest.raises(ConfigError, match="is a directory"):
        parse_config(str(tmp_path))


def test_file_without_read_permission(tmp_path: Path) -> None:
    """A file that cannot be read gives a clear error."""
    path = Path(write_config(tmp_path, VALID))
    path.chmod(0o000)
    try:
        if can_read(path):
            pytest.skip("running as root: permissions are not enforced")
        with pytest.raises(ConfigError, match="permission denied"):
            parse_config(str(path))
    finally:
        path.chmod(0o644)


def test_wrong_number_of_arguments(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Without exactly one argument the usage line is shown."""
    assert main([]) == 1
    assert main(["a.txt", "b.txt"]) == 1
    assert "Usage: python3 a_maze_ing.py config.txt" in capsys.readouterr().err


def test_default_config_is_valid() -> None:
    """The config.txt shipped with the repository is accepted."""
    config = parse_config(str(ROOT / "config.txt"))
    assert config == MazeConfig(
        width=20,
        height=15,
        entry=(0, 0),
        exit=(19, 14),
        output_file="maze.txt",
        perfect=True,
        seed=42,
    )


def test_spaces_comments_and_lowercase_bool(tmp_path: Path) -> None:
    """Spaces around '=', blank lines, comments and 'false' are fine."""
    text = (
        "# comment\n"
        "\n"
        "WIDTH = 10\n"
        "  HEIGHT=8  \n"
        "ENTRY= 1, 2\n"
        "EXIT =9,7\n"
        "OUTPUT_FILE=out.txt\n"
        "PERFECT=false\n"
    )
    config = parse_config(write_config(tmp_path, text))
    assert (config.width, config.height) == (10, 8)
    assert config.entry == (1, 2)
    assert config.exit == (9, 7)
    assert config.perfect is False
    assert config.seed is None


def test_file_with_bom(tmp_path: Path) -> None:
    """A file saved with a UTF-8 BOM (Windows editors) is accepted."""
    path = tmp_path / "bom.txt"
    path.write_bytes(b"\xef\xbb\xbf" + VALID.encode("utf-8"))
    assert parse_config(str(path)).width == 20


def test_unknown_key_is_a_warning(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An unknown key is ignored, with a warning on stderr."""
    config = parse_config(write_config(tmp_path, VALID + "ALGO=dfs\n"))
    assert config.width == 20
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "line 7: unknown key 'ALGO'" in captured.err


def test_long_value_is_cut_in_message(tmp_path: Path) -> None:
    """A huge value is not copied whole into the error message."""
    text = VALID.replace("WIDTH=20", "WIDTH=" + "9" * 5000)
    with pytest.raises(ConfigError) as info:
        parse_config(write_config(tmp_path, text))
    message = str(info.value)
    assert message.endswith("...")
    assert len(message) < MAX_SHOWN_VALUE + 60

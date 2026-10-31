"""Tests for the interactive menu (subject, chapter V)."""

from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

from a_maze_ing import main
from app.config import MazeConfig
from app.menu import Action, MenuState, build_maze, parse_choice, run_menu
from app.render import PALETTES, RenderState
from mazegen import MazeGenerator


def make_config(tmp_path: Path, width: int = 20, height: int = 15,
                seed: int | None = 42) -> MazeConfig:
    """Config with the entry and exit in opposite corners."""
    return MazeConfig(width=width, height=height, entry=(0, 0),
                      exit=(width - 1, height - 1),
                      output_file=str(tmp_path / "maze.txt"),
                      perfect=True, seed=seed)


def make_state(tmp_path: Path, **kwargs: int) -> MenuState:
    config = make_config(tmp_path, **kwargs)
    return MenuState(config=config, maze=build_maze(config, config.seed))


def feed(*answers: str | type[BaseException]) -> Callable[[str], str]:
    """Fake ``input``: returns the answers in order, raising exceptions."""
    it: Iterator[str | type[BaseException]] = iter(answers)

    def read(prompt: str) -> str:
        answer = next(it, EOFError)
        if isinstance(answer, str):
            return answer
        raise answer
    return read


def no_display(maze: MazeGenerator, view: RenderState) -> None:
    """Skip the drawing in tests."""


def hex_rows(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").split("\n")
    return lines[:lines.index("")]


@pytest.mark.parametrize("text, action", [
    ("1", Action.REGENERATE), (" 2 ", Action.TOGGLE_PATH),
    ("3\n", Action.NEXT_COLORS), ("4", Action.QUIT),
])
def test_valid_choices(text: str, action: Action) -> None:
    assert parse_choice(text) is action


@pytest.mark.parametrize("text", [
    "", "   ", "0", "5", "-1", "12", "a", "quit", "1.0", "\x00", "１",
])
def test_garbage_is_not_a_choice(text: str) -> None:
    assert parse_choice(text) is None


def test_quit(tmp_path: Path) -> None:
    state = make_state(tmp_path)
    run_menu(state, read=feed("4"), show=no_display)
    assert not state.running


@pytest.mark.parametrize("error", [EOFError, KeyboardInterrupt])
def test_ctrl_d_and_ctrl_c_quit(tmp_path: Path,
                                error: type[BaseException]) -> None:
    state = make_state(tmp_path)
    run_menu(state, read=feed("2", error), show=no_display)
    assert not state.running


def test_invalid_input_asks_again(tmp_path: Path) -> None:
    state = make_state(tmp_path)
    messages: list[str] = []

    def show(maze: MazeGenerator, view: RenderState) -> None:
        messages.append(state.message)

    run_menu(state, read=feed("", "abc", "9", "4"), show=show)
    assert not state.running
    assert "Invalid choice" in messages[-1]
    assert sum("Invalid choice" in m for m in messages) == 3


def test_toggle_path(tmp_path: Path) -> None:
    state = make_state(tmp_path)
    assert state.view.show_path
    run_menu(state, read=feed("2"), show=no_display)
    assert not state.view.show_path
    state = make_state(tmp_path)
    run_menu(state, read=feed("2", "2"), show=no_display)
    assert state.view.show_path


def test_change_colours_cycles(tmp_path: Path) -> None:
    state = make_state(tmp_path)
    names = []

    def show(maze: MazeGenerator, view: RenderState) -> None:
        names.append(view.palette.name)

    run_menu(state, read=feed(*["3"] * len(PALETTES)), show=show)
    assert names[:len(PALETTES)] == [p.name for p in PALETTES]
    assert names[-1] == PALETTES[0].name


def test_regenerate_changes_maze_and_rewrites_file(tmp_path: Path) -> None:
    state = make_state(tmp_path)
    out = Path(state.config.output_file)
    seeds = []

    def show(maze: MazeGenerator, view: RenderState) -> None:
        seeds.append(maze.seed)

    run_menu(state, read=feed("1", "1"), show=show)
    assert len(set(seeds)) == 3
    maze = state.maze
    assert hex_rows(out) == ["".join(f"{c:x}" for c in row)
                             for row in maze.grid]
    assert out.read_text().endswith(maze.solution_directions + "\n")


def test_regenerate_keeps_display_options(tmp_path: Path) -> None:
    state = make_state(tmp_path)
    run_menu(state, read=feed("2", "3", "1"), show=no_display)
    assert not state.view.show_path
    assert state.view.palette_index == 1


def test_regenerate_with_unwritable_file_does_not_crash(
    tmp_path: Path,
) -> None:
    state = make_state(tmp_path)
    state.config = make_config(tmp_path / "missing_dir")
    run_menu(state, read=feed("1"), show=no_display)
    assert "WriteError" in state.message


def test_small_maze_reports_missing_42(tmp_path: Path) -> None:
    state = make_state(tmp_path, width=4, height=4)
    run_menu(state, read=feed("1"), show=no_display)
    assert "too small" in state.message


def test_main_with_empty_stdin_exits_cleanly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config = tmp_path / "config.txt"
    config.write_text(
        "WIDTH=20\nHEIGHT=15\nENTRY=0,0\nEXIT=19,14\n"
        f"OUTPUT_FILE={tmp_path / 'maze.txt'}\nPERFECT=True\nSEED=1\n"
    )
    answers = feed("x", "1", "2", "3")
    monkeypatch.setattr("builtins.input", answers)
    assert main([str(config)]) == 0
    assert (tmp_path / "maze.txt").exists()
    assert "Bye!" in capsys.readouterr().out

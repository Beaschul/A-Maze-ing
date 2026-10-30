"""Tests for the terminal ASCII renderer (subject, chapter V)."""

import os
from pathlib import Path

import pytest

from app.render import (
    BLOCK,
    PALETTES,
    RESET,
    Layer,
    RenderState,
    build_layers,
    display,
    render,
)
from mazegen import Direction, MazeGenerator
from mazegen.writer import write_output


def make_maze(width: int = 20, height: int = 15, seed: int = 42,
              perfect: bool = True) -> MazeGenerator:
    """Generate a maze with the entry and exit in opposite corners."""
    maze = MazeGenerator(width, height, entry=(0, 0),
                         exit=(width - 1, height - 1),
                         perfect=perfect, seed=seed)
    maze.generate()
    return maze


def read_hex_grid(path: Path) -> list[list[int]]:
    """Read the wall masks back from an output file."""
    lines = path.read_text(encoding="utf-8").split("\n")
    rows = lines[:lines.index("")]
    return [[int(char, 16) for char in row] for row in rows]


def write_maze(maze: MazeGenerator, path: Path) -> None:
    """Write ``maze`` exactly like a_maze_ing.py does."""
    write_output(
        path,
        hex_rows=["".join(f"{c:x}" for c in row) for row in maze.grid],
        entry=maze.entry,
        exit=maze.exit,
        path_moves=maze.solution_directions,
    )


def test_matrix_is_2h_plus_1_by_2w_plus_1() -> None:
    layers = build_layers(make_maze(7, 4, seed=1), show_path=True)
    assert len(layers) == 9
    assert all(len(row) == 15 for row in layers)


@pytest.mark.parametrize("perfect", [True, False])
@pytest.mark.parametrize("width, height, seed", [
    (3, 2, 0), (5, 5, 7), (20, 15, 42), (31, 9, 123),
])
def test_walls_match_output_file(tmp_path: Path, width: int, height: int,
                                 seed: int, perfect: bool) -> None:
    maze = make_maze(width, height, seed, perfect)
    out = tmp_path / "maze.txt"
    write_maze(maze, out)
    grid = read_hex_grid(out)
    layers = build_layers(maze, show_path=False)

    def drawn(row: int, col: int) -> bool:
        # Walls inside the "42" are drawn with the pattern colour.
        return layers[row][col] in (Layer.WALL, Layer.PATTERN)

    for y in range(height):
        for x in range(width):
            mask = grid[y][x]
            assert drawn(2 * y, 2 * x + 1) == bool(mask & Direction.NORTH)
            assert drawn(2 * y + 2, 2 * x + 1) == bool(mask & Direction.SOUTH)
            assert drawn(2 * y + 1, 2 * x) == bool(mask & Direction.WEST)
            assert drawn(2 * y + 1, 2 * x + 2) == bool(mask & Direction.EAST)


def test_small_maze_checked_by_hand(tmp_path: Path) -> None:
    # 3x2, seed 0: output file "b93\nc6e", path "SENE"
    #   b = N+E+W   9 = N+W     3 = N+E
    #   c = S+W     6 = E+S     e = E+S+W
    maze = MazeGenerator(3, 2, entry=(0, 0), exit=(2, 0), seed=0)
    maze.generate()
    out = tmp_path / "maze.txt"
    write_maze(maze, out)
    assert out.read_text(encoding="utf-8") == "b93\nc6e\n\n0,0\n2,0\nSENE\n"

    symbols = {Layer.WALL: "#", Layer.OPEN: ".", Layer.ENTRY: "E",
               Layer.EXIT: "X", Layer.PATH: "*"}
    picture = [
        "".join(symbols[layer] for layer in row)
        for row in build_layers(maze, show_path=True)
    ]
    assert picture == [
        "#######",
        "#E#**X#",
        "#*#*#.#",
        "#***#.#",
        "#######",
    ]


def test_entry_and_exit_are_drawn_once() -> None:
    flat = [layer for row in build_layers(make_maze(), True)
            for layer in row]
    assert flat.count(Layer.ENTRY) == 1
    assert flat.count(Layer.EXIT) == 1


def test_entry_and_exit_are_on_their_cells() -> None:
    maze = make_maze()
    layers = build_layers(maze, show_path=True)
    ex, ey = maze.exit
    assert layers[1][1] is Layer.ENTRY
    assert layers[2 * ey + 1][2 * ex + 1] is Layer.EXIT


def test_pattern_42_is_drawn_on_its_cells() -> None:
    maze = make_maze()
    layers = build_layers(maze, show_path=True)
    assert maze.pattern_cells
    for x, y in maze.pattern_cells:
        assert layers[2 * y + 1][2 * x + 1] is Layer.PATTERN


def test_walls_between_pattern_cells_use_pattern_colour() -> None:
    maze = make_maze()
    layers = build_layers(maze, show_path=True)
    pattern = maze.pattern_cells
    pairs = [(x, y) for x, y in pattern if (x + 1, y) in pattern]
    assert pairs
    for x, y in pairs:
        assert layers[2 * y + 1][2 * x + 2] is Layer.PATTERN


def test_no_pattern_when_maze_is_too_small() -> None:
    flat = [layer for row in build_layers(make_maze(4, 4, seed=3), True)
            for layer in row]
    assert Layer.PATTERN not in flat


def test_path_covers_solution_and_passages() -> None:
    maze = make_maze()
    layers = build_layers(maze, show_path=True)
    path = maze.solution
    for x, y in path[1:-1]:
        assert layers[2 * y + 1][2 * x + 1] is Layer.PATH
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        assert layers[y1 + y2 + 1][x1 + x2 + 1] is Layer.PATH
    flat = [layer for row in layers for layer in row]
    assert flat.count(Layer.PATH) == 2 * len(path) - 3


def test_hidden_path_is_not_drawn() -> None:
    flat = [layer for row in build_layers(make_maze(), show_path=False)
            for layer in row]
    assert Layer.PATH not in flat
    assert Layer.ENTRY in flat and Layer.EXIT in flat


def test_every_layer_has_its_own_colour() -> None:
    maze = make_maze()
    for index in range(len(PALETTES)):
        palette = PALETTES[index]
        others = {"93", "92", "91"}  # path, entry, exit
        assert palette.wall != palette.pattern
        assert not {palette.wall, palette.pattern} & others
        text = render(maze, RenderState(palette_index=index))
        for code in {palette.wall, palette.pattern} | others:
            assert f"\033[{code}m{BLOCK}" in text


def test_every_line_resets_colours() -> None:
    text = render(make_maze(), RenderState())
    assert all(line.endswith(RESET) for line in text.split("\n"))


def test_palette_rotation_cycles() -> None:
    state = RenderState()
    names = []
    for _ in range(len(PALETTES) + 1):
        names.append(state.palette.name)
        state.next_palette()
    assert names[0] == names[-1]
    assert len(set(names)) == len(PALETTES)


def test_toggle_path() -> None:
    state = RenderState()
    state.toggle_path()
    assert not state.show_path
    state.toggle_path()
    assert state.show_path


def test_maze_bigger_than_terminal_warns_without_crashing(
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr("shutil.get_terminal_size",
                        lambda *args: os.terminal_size((20, 10)))
    display(make_maze(), RenderState())
    out = capsys.readouterr().out
    assert "bigger than the terminal" in out
    assert BLOCK in out


def test_maze_fitting_terminal_has_no_warning(
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr("shutil.get_terminal_size",
                        lambda *args: os.terminal_size((200, 100)))
    display(make_maze(), RenderState())
    assert "bigger than the terminal" not in capsys.readouterr().out

"""A-Maze-ing — entry point."""

from __future__ import annotations

import sys

from app.config import parse_config
from app.errors import ConfigError
from mazegen.maze_generator import MazeGenerator
from mazegen.errors import MazeError
from mazegen.writer import write_output


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

    # 1. Ler e validar o config
    try:
        config = parse_config(argv[0])
    except ConfigError as exc:
        print(f"ConfigError: {exc}", file=sys.stderr)
        return 1

    # 2. Gerar o labirinto
    try:
        maze = MazeGenerator(
            width=config.width,
            height=config.height,
            entry=config.entry,
            exit=config.exit,
            perfect=config.perfect,
            seed=config.seed,
        )
        maze.generate()
    except MazeError as exc:
        print(f"MazeError: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 — safety net
        print(f"Unexpected generation error: {exc}", file=sys.stderr)
        return 1

    # 3. Escrever o arquivo de saída (Task #9)
    try:
        # Como o seu MazeGenerator tem a propriedade .grid (list[list[int]]),
        # precisamos converter para hexadecimal.
        # O seu gerador usa a convenção: N=1, E=2, S=4, W=8.
        # O subject pede exatamente isso!
        hex_rows = [
            "".join(f"{cell:x}" for cell in row) 
            for row in maze.grid
        ]
        
        write_output(
            path=config.output_file,
            hex_rows=hex_rows,
            entry=config.entry,
            exit=config.exit,
            path_moves=maze.solution_directions,
        )
    except OSError as exc:
        print(f"WriteError: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Unexpected write error: {exc}", file=sys.stderr)
        return 1

    print(f"OK: Maze {config.width}x{config.height} generated successfully!")
    print(f"Output written to: {config.output_file}")
    print(f"Shortest path length: {len(maze.solution_directions)} steps")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
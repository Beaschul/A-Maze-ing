"""Exceptions raised by the mazegen package."""


class MazeError(Exception):
    """Raised when a maze cannot be built or queried.

    Examples: invalid size, entry/exit outside the maze or on the "42"
    pattern, reading the solution before generating the maze.
    """

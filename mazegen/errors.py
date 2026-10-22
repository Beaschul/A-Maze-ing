class ConfigError(Exception):
    """Raised when a configuration file is invalid.

    Attributes:
        line: The 1-based line number where the error was found, or None
              if the error is not tied to a specific line.
    """

    def __init__(self, message: str, line: int | None = None) -> None:
        """Build a ConfigError.

        Args:
            message: Human-readable description of the problem.
            line: Optional 1-based line number where the problem occurred.
        """
        self.line = line
        if line is not None:
            super().__init__(f"line {line}: {message}")
        else:
            super().__init__(message)
"""Exceptions raised by the mazegen package."""


class MazeError(Exception):
    """Raised when a maze cannot be built or queried.

    Examples: invalid size, entry/exit outside the maze or on the "42"
    pattern, reading the solution before generating the maze.
    """

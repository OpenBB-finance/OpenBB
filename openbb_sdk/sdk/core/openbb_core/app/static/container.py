"""Container class."""
from openbb_core.app.command_runner import CommandRunner


class Container:
    """Container class for the command runner session."""

    def __init__(self, command_runner: CommandRunner) -> None:
        self._command_runner = command_runner

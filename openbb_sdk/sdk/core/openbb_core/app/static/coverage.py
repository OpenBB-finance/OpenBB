"""Coverage module."""
from openbb_core.app.router import CommandMap


class Coverage:
    """/coverage
    providers
    commands"""

    def __init__(self):
        self._command_map = CommandMap(coverage_sep=".")

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def providers(self):
        """Return providers coverage."""
        return self._command_map.provider_coverage

    @property
    def commands(self):
        """Return commands coverage."""
        return self._command_map.command_coverage

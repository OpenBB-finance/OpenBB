"""Coverage module."""
from openbb_core.app.router import CommandMap


class Coverage:
    """Coverage class."""

    def __init__(self):
        self._command_map = CommandMap(coverage_sep=".")

    @property
    def providers(self):
        """Return providers coverage."""
        return self._command_map.provider_coverage

    @property
    def commands(self):
        """Return commands coverage."""
        return self._command_map.command_coverage

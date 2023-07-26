"""Coverage module."""
from openbb_core.app.router import CommandMap


class Coverage:
    """Coverage class."""

    def __init__(self):
        self.__command_map = CommandMap()

    @property
    def providers(self):
        """Return providers coverage."""
        return self.__command_map.provider_coverage

    @property
    def commands(self):
        """Return commands coverage."""
        return self.__command_map.command_coverage

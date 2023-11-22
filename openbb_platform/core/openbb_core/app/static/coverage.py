"""Coverage module."""
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.router import CommandMap


class Coverage:
    """/coverage

    providers
    commands
    command_model
    """

    def __init__(self):
        """Initialize coverage."""
        self._command_map = CommandMap(coverage_sep=".")
        self._provider_interface = ProviderInterface()

    def __repr__(self) -> str:
        """Return docstring."""
        return self.__doc__ or ""

    @property
    def providers(self):
        """Return providers coverage."""
        return self._command_map.provider_coverage

    @property
    def commands(self):
        """Return commands coverage."""
        return self._command_map.command_coverage

    @property
    def command_model(self):
        """Return command to model mapping."""
        return {
            command: self._provider_interface.map[
                self._command_map.commands_model[command]
            ]
            for command in self._command_map.commands_model  # pylint: disable=C0206
        }

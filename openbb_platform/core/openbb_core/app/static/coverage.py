"""Coverage module."""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from openbb_core.api.router.helpers.coverage_helpers import get_route_schema_map
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.router import CommandMap
from openbb_core.app.static.reference_loader import ReferenceLoader

if TYPE_CHECKING:
    from openbb_core.app.static.app_factory import BaseApp


class Coverage:  # noqa: D205, D400
    """/coverage
    providers
    commands
    command_model
    command_schemas
    reference
    """

    def __init__(self, app: "BaseApp"):
        """Initialize coverage."""
        self._app = app
        self._command_map = CommandMap(coverage_sep=".")
        self._provider_interface = ProviderInterface()
        self._reference_loader = ReferenceLoader()

    def __repr__(self) -> str:
        """Return docstring."""
        return self.__doc__ or ""

    @property
    def providers(self) -> Dict[str, List[str]]:
        """Return providers coverage."""
        return self._command_map.provider_coverage

    @property
    def commands(self) -> Dict[str, List[str]]:
        """Return commands coverage."""
        return self._command_map.command_coverage

    @property
    def command_model(self) -> Dict[str, Dict[str, Dict[str, Dict[str, Any]]]]:
        """Return command to model mapping."""
        return {
            command: self._provider_interface.map[value]
            for command, value in self._command_map.commands_model.items()
        }

    @property
    def reference(self) -> Dict[str, Dict]:
        """Return reference data."""
        return self._reference_loader.reference

    def command_schemas(self, filter_by_provider: Optional[str] = None):
        """Return route schema for a command."""
        return get_route_schema_map(
            self._app, self._command_map.commands_model, filter_by_provider
        )

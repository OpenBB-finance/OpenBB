"""Container class."""

from typing import Any, Optional

from openbb_core.app.command_runner import CommandRunner
from openbb_core.app.model.obbject import OBBject


class Container:
    """Container class for the command runner session."""

    def __init__(self, command_runner: CommandRunner) -> None:
        self._command_runner = command_runner
        OBBject._credentials = command_runner.user_settings.credentials

    def _run(self, *args, **kwargs) -> Any:
        """Run a command in the container."""
        obbject = self._command_runner.sync_run(*args, **kwargs)
        output_type = self._command_runner.user_settings.preferences.output_type
        if output_type == "OBBject":
            return obbject
        return getattr(obbject, "to_" + output_type)()

    def _get_provider(self, choice: Optional[str], cmd: str, default: str) -> str:
        """Get the provider to use in execution."""
        if choice is None:
            if config_default := self._command_runner.user_settings.defaults.routes.get(
                cmd, {}
            ).get("provider"):
                return config_default
            return default
        return choice

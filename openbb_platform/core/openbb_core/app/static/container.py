"""Container class."""

from typing import Any, Optional, Tuple

from openbb_core.app.command_runner import CommandRunner
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.obbject import OBBject


class Container:
    """Container class for the command runner session."""

    def __init__(self, command_runner: CommandRunner) -> None:
        """Initialize the container."""
        self._command_runner = command_runner
        OBBject._user_settings = command_runner.user_settings
        OBBject._system_settings = command_runner.system_settings

    def _run(self, *args, **kwargs) -> Any:
        """Run a command in the container."""
        obbject = self._command_runner.sync_run(*args, **kwargs)
        output_type = self._command_runner.user_settings.preferences.output_type
        if output_type == "OBBject":
            return obbject
        return getattr(obbject, "to_" + output_type)()

    def _check_credentials(self, provider: str) -> bool:
        """Check required credentials are populated."""
        credentials = self._command_runner.user_settings.credentials
        if provider not in credentials.origins:
            return False
        required = credentials.origins.get(provider)
        return all(getattr(credentials, r, None) for r in required)

    def _get_provider(
        self, choice: Optional[str], cmd: str, available: Tuple[str, ...]
    ) -> str:
        """Get the provider to use in execution."""
        if choice is None:
            routes = self._command_runner.user_settings.defaults.routes
            provider = routes.get(cmd, {}).get("provider", []) or available
            providers = [provider] if isinstance(provider, str) else provider
            for p in providers:
                if self._check_credentials(p):
                    return p
            raise OpenBBError(
                f"Please specify the provider. Fallback failed, tried -> {', '.join(providers)}."
            )
        return choice

"""Container class."""

from typing import Any, Optional, Tuple

from openbb_core.app.command_runner import CommandRunner
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
        required = credentials.providers.get(provider, [])
        current = credentials.model_dump(exclude_none=True)
        return all(item in current for item in required)

    def _get_provider(
        self, choice: Optional[str], cmd: str, available: Tuple[str, ...]
    ) -> str:
        """Get the provider to use in execution."""
        if choice is None:
            routes = self._command_runner.user_settings.defaults.routes
            if provider := (routes.get(cmd, {}).get("provider") or available):
                provider_iterable = (
                    [provider] if isinstance(provider, str) else provider
                )
                for p in provider_iterable:
                    if self._check_credentials(p):
                        return p
                    continue
            # Warn that that no provider with keys was found
            # We fallback to the first provider that does not need keys
            # We fallback to the first provider
            return available[0]
        return choice

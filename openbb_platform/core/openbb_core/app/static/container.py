"""Container class."""

from typing import TYPE_CHECKING, Any, Optional

from openbb_core.app.model.abstract.error import OpenBBError

if TYPE_CHECKING:
    from openbb_core.app.command_runner import CommandRunner


class Container:
    """Container class for the command runner session."""

    def __init__(self, command_runner: "CommandRunner") -> None:
        """Initialize the container."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.model.obbject import OBBject

        self._command_runner = command_runner
        OBBject._user_settings = command_runner.user_settings
        OBBject._system_settings = command_runner.system_settings

    def _run(self, *args, **kwargs) -> Any:
        """Run a command in the container."""
        endpoint = args[0][1:].replace("/", ".") if args else ""
        defaults = self._command_runner.user_settings.defaults.commands

        if endpoint and defaults and defaults.get(endpoint):
            default_params = {
                k: v for k, v in defaults[endpoint].items() if k != "provider"
            }
            for k, v in default_params.items():
                if k == "chart" and v is True:
                    kwargs["chart"] = True
                elif (
                    k in kwargs["standard_params"]
                    and kwargs["standard_params"][k] is None
                ):
                    kwargs["standard_params"][k] = v
                elif (
                    k in kwargs["extra_params"] and kwargs["extra_params"][k] is None
                ) or k not in kwargs["extra_params"]:
                    kwargs["extra_params"][k] = v

        obbject = self._command_runner.sync_run(*args, **kwargs)
        output_type = self._command_runner.user_settings.preferences.output_type
        if output_type == "OBBject":
            return obbject
        return getattr(obbject, "to_" + output_type)()

    def _check_credentials(self, provider: str) -> Optional[bool]:
        """Check required credentials are populated."""
        credentials = self._command_runner.user_settings.credentials
        if provider not in credentials.origins:
            return None
        required = credentials.origins.get(provider)
        return all(getattr(credentials, r, None) for r in required)

    def _get_provider(
        self, choice: Optional[str], command: str, default_priority: tuple[str, ...]
    ) -> str:
        """Get the provider to use in execution.

        If no choice is specified, the configured priority list is used. A provider is used
        when all of its required credentials are populated.

        Parameters
        ----------
        choice: Optional[str]
            The provider choice, for example 'fmp'.
        command: str
            The command to get the provider for, for example 'equity.price.historical'
        default_priority: Tuple[str, ...]
            A tuple of available providers for the given command to use as default priority list.

        Returns
        -------
        str
            The provider to use in the command.

        Raises
        ------
        OpenBBError
            Raises error when all the providers in the priority list failed.
        """
        if choice is None:
            commands = self._command_runner.user_settings.defaults.commands
            providers = (
                commands.get(command, {}).get("provider", []) or default_priority
            )
            tries = []
            if len(providers) == 1:
                return providers[0]
            for p in providers:
                result = self._check_credentials(p)
                if result:
                    return p
                if result is False:
                    tries.append((p, "missing credentials"))
                else:
                    tries.append((p, f"not installed, please install openbb-{p}"))

            msg = "\n  ".join([f"* '{pair[0]}' -> {pair[1]}" for pair in tries])
            raise OpenBBError(f"Provider fallback failed.\n" f"[Providers]\n  {msg}")
        return choice

"""Container class."""
from openbb_core.app.command_runner import CommandRunner
from openbb_core.app.model.obbject import OBBject


class Container:
    """Container class for the command runner session."""

    def __init__(self, command_runner: CommandRunner) -> None:
        self._command_runner = command_runner

    def run(self, *args, **kwargs) -> OBBject:
        """Run a command in the container."""
        obbject = self._command_runner.run(*args, **kwargs)
        user_settings = self._command_runner.user_settings
        python_output = user_settings.preferences.python_output
        if python_output:
            return getattr(obbject, python_output)()
        obbject.extra["user_settings"] = user_settings.dict()
        return obbject

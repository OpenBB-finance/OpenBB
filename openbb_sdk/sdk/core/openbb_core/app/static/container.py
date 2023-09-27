"""Container class."""
from typing import Union
from openbb_core.app.command_runner import CommandRunner
from openbb_core.app.model.obbject import OBBject
import pandas as pd


class Container:
    """Container class for the command runner session."""

    def __init__(self, command_runner: CommandRunner) -> None:
        self._command_runner = command_runner

    def run(self, *args, **kwargs) -> Union[OBBject, pd.DataFrame, dict]:
        """Run a command in the container."""
        obbject = self._command_runner.run(*args, **kwargs)
        python_output = self._command_runner.user_settings.preferences.python_output
        if python_output:
            return getattr(obbject, python_output)()
        return obbject

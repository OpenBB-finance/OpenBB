"""Container class."""
from typing import Union

import pandas as pd

from openbb_core.app.command_runner import CommandRunner
from openbb_core.app.model.obbject import OBBject


class Container:
    """Container class for the command runner session."""

    def __init__(self, command_runner: CommandRunner) -> None:
        self._command_runner = command_runner

    def run(self, *args, **kwargs) -> Union[OBBject, pd.DataFrame, dict]:
        """Run a command in the container."""
        obbject = self._command_runner.run(*args, **kwargs)
        obbject_method = self._command_runner.user_settings.preferences.obbject_method
        if obbject_method:
            return getattr(obbject, obbject_method)()
        return obbject

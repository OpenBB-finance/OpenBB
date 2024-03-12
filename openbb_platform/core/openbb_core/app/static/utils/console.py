"""Console module."""

from openbb_core.env import Env


class Console:
    """Console to be used by builder and linters."""

    def __init__(self, verbose: bool):
        """Initialize the console."""
        self.verbose = verbose

    def log(self, message: str, **kwargs):
        """Console log method."""
        if self.verbose or Env().DEBUG_MODE:
            print(message, **kwargs)  # noqa: T201

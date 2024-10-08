"""Empty OBBject extension."""

import warnings

from openbb_core.app.model.extension import Extension
from openbb_core.app.model.obbject import OBBject

warnings.filterwarnings(
    "ignore", lineno=0
)  # This suppresses a warning you might see with IPython and OBBject Extensions on import and initialize.

ext = Extension(name="empty")

# OBBject Accessors are used to extend the functionality of the OBBject class.
# The name given to the Extension creates a new namespace in every output object of the Router.
# This is useful for formatting/processing the output of the function calls, where universal application is desired.


@ext.obbject_accessor
class Empty:
    """An Empty OBBject extension."""

    def __init__(self, obbject):
        """Creates an instance of the Empty OBBject extension."""
        self._obbject: OBBject = obbject

    @staticmethod
    def hello():
        """Print a greeting message."""
        print("Hello from the Empty OBBject extension!")  # noqa: T201

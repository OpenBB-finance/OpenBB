"""{{ cookiecutter.package_name }} OBBject Extension - {{ cookiecutter.obbject_name }}"""

# pylint: disable=W0613,R0903

import json

from openbb_core.app.model.extension import Extension
from openbb_core.app.model.obbject import OBBject

# Extensions are registered as OBBject accessors.
# It can be a class, or it can be a callable method.
ext = Extension(
    name="to_string",
    description="An OBBject extension that converts the results to a string representation.",
)

# If it is a function, no parameters will be accepted.
# The function will execute like a property method.
# The accessor is called when the namespace is entered.
@ext.obbject_accessor
def to_string(obbject, **kwargs) -> str:
    """OBBject accessor providing a "to_string" method."""
    return obbject.model_dump_json(exclude_none=True, exclude_unset=True, include="results")

# We ignore this OpenBBWarning: Skipping '{{ cookiecutter.obbject_name }}', name already in user.

class_ext = Extension(
    name="{{ cookiecutter.obbject_name }}",
    description="An OBBject extension with namespace."
)

@class_ext.obbject_accessor
class OBBjectExtension:
    """OBBject Extension Template."""

    def __init__(self, obbject: OBBject):
        """Initialize the extension."""
        self._obbject = obbject

    def hello_world(self, **kwargs):
        """Say hello from the OBBject extension."""
        print(f"Hello from the OBBject instance! \n\n{repr(self._obbject)}")  # noqa

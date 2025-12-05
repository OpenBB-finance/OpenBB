"""{{ cookiecutter.package_name }} OBBject Extension - {{ cookiecutter.obbject_name }}"""

# pylint: disable=W0613,R0903

import threading
import time

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

## Non-blocking OBBject Extension Example
## Uncomment to use
#nonblocking_plugin = Extension(
#    name="nonblocking_plugin",
#    description="An on-command-output plugin simulating an extensive task performed in a separate thread.",
#    on_command_output=True,  # Must be set as True
#    command_output_paths=["/{{cookiecutter.router_name}}/candles"],
#    immutable=True,  # Set to `True` for parallel processing.
#    results_only=False,  # Use this as a flag to return only the "results" portion of the OBBject.
#)


#def _expensive_operation_worker(serialized_obbject: dict):
#    """Simulate a long-running task without blocking the caller."""
#    working_copy = OBBject(**serialized_obbject)
#    print("\nThis is the deserialized OBBject in the non-blocking thread.")
#    print(working_copy.__repr__())
#    for i in range(10):
#        print(str(i) + " seconds remaining...")
#        time.sleep(1)
#    print("Expensive operation is now complete.")


#@nonblocking_plugin.obbject_accessor
#def empty_plugin_function(obbject):  # This can also be an async function.
#    """Simulated on_commnd_output function that executes an expensive task
#    in a non-blocking thread."""
#    print(
#        "Serializing the obbject and passing to a new thread.\n"
#        f"Command executed: {obbject.extra['metadata']}\n"
#    )
#    print(
#        "Simulating an expensive task that is non-blocking and allows the function to return."
#    )
#    threading.Thread(
#        target=_expensive_operation_worker,
#        args=(obbject.model_dump(),),
#        name="empty-plugin-expensive-operation",
#        daemon=False,
#    ).start()

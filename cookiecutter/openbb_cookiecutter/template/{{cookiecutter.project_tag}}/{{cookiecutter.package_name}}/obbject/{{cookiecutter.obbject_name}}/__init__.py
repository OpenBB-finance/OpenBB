{%- set types = cookiecutter.extension_types.split(',') | map('trim') | list -%}
{%- set has_obbject = 'obbject' in types or 'all' in types -%}
"""{{ cookiecutter.obbject_name }} OBBject extensions."""
{%- if has_obbject %}

from openbb_core.app.model.extension import Extension
from openbb_core.app.model.obbject import OBBject

ext = Extension(
    name="to_string",
    description="Serialize the results of an OBBject to a JSON string.",
)


@ext.obbject_accessor
def to_string(obbject: OBBject) -> str:
    """Return the results as a JSON string, read as ``obbject.to_string``.

    Parameters
    ----------
    obbject : OBBject
        The command output.

    Returns
    -------
    str
        The results serialized as JSON.
    """
    return obbject.model_dump_json(
        exclude_none=True, exclude_unset=True, include={"results"}
    )


class_ext = Extension(
    name="{{ cookiecutter.obbject_name }}",
    description="A namespace of methods on every OBBject.",
)


@class_ext.obbject_accessor
class OBBjectExtension:
    """Methods available as ``obbject.{{ cookiecutter.obbject_name }}``."""

    def __init__(self, obbject: OBBject):
        """Bind the extension to a command output.

        Parameters
        ----------
        obbject : OBBject
            The command output.
        """
        self._obbject = obbject

    def hello_world(self) -> str:
        """Return a greeting that names the command's provider.

        Returns
        -------
        str
            The greeting.
        """
        return f"Hello from the OBBject returned by {self._obbject.provider}!"
{%- endif %}

"""OpenBB Workspace Query Models."""

from openbb_core.provider.abstract.data import Data
from pydantic import AliasGenerator, ConfigDict
from pydantic.alias_generators import to_snake


class FormData(Data):
    """Submit a form via POST request."""

    model_config = ConfigDict(
        extra="allow",
        alias_generator=AliasGenerator(to_snake),
        title="Submit Form",
    )

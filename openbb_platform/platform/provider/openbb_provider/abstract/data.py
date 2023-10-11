"""The OpenBB Standardized Data Model."""

from typing import Dict

from pydantic import BaseModel, ConfigDict, alias_generators, model_validator
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated


def check_int(v: int) -> int:
    try:
        return int(v)
    except ValueError as exc:
        raise TypeError("value must be an int") from exc


StrictInt = Annotated[int, BeforeValidator(check_int)]


class Data(BaseModel):
    """The OpenBB Standardized Data Model."""

    __alias_dict__: Dict[str, str] = {}

    def __repr__(self):
        """Return a string representation of the object."""
        return f"{self.__class__.__name__}({', '.join([f'{k}={v}' for k, v in super().model_dump().items()])})"

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        alias_generator=alias_generators.to_camel,
        strict=False,
    )

    @model_validator(mode="before")
    @classmethod
    def _use_alias(cls, values):
        """Use alias for error locs."""
        # set the alias dict values keys
        aliases = {orig: alias for alias, orig in cls.__alias_dict__.items()}
        if aliases:
            return {aliases.get(k, k): v for k, v in values.items()}

        return values

"""The OpenBB Standardized Data Model."""

from typing import Annotated, Dict

from pydantic import (
    BaseModel,
    ConfigDict,
    Extra,
    alias_generators,
    model_validator,
)
from pydantic.functional_validators import BeforeValidator


def check_int(v: int) -> int:
    try:
        return int(v)
    except ValueError:
        raise TypeError("value must be an int")


StrictInt = Annotated[int, BeforeValidator(check_int)]


class Data(BaseModel):
    """The OpenBB Standardized Data Model."""

    __alias_dict__: Dict[str, str] = {}

    def __repr__(self):
        """Return a string representation of the object."""
        return f"{self.__class__.__name__}({', '.join([f'{k}={v}' for k, v in super().model_dump().items()])})"

    model_config = ConfigDict(
        extra=Extra.allow,
        populate_by_name=True,
        alias_generator=alias_generators.to_camel,
        strict=False,
    )

    @model_validator(mode="before")
    @classmethod
    def _use_alias(cls, values):
        """Use alias for error locs."""
        # set the alias dict values keys
        alises = {orig: alias for alias, orig in cls.__alias_dict__.items()}
        if alises:
            return {alises.get(k, k): v for k, v in values.items()}

        return values

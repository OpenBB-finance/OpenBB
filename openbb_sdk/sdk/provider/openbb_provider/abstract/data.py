"""The OpenBB Standardized Data Model."""
from pydantic import BaseModel, Extra

from openbb_provider.utils.helpers import to_camel_case, to_snake_case


class Data(BaseModel):
    """The OpenBB Standardized Data Model."""

    def dict(self, *args, **kwargs):
        original_dict = super().dict(*args, **kwargs)
        return {to_snake_case(k): v for k, v in original_dict.items()}

    def __repr__(self):
        """Return a string representation of the object."""
        return f"{self.__class__.__name__}({', '.join([f'{k}={v}' for k, v in super().dict().items()])})"

    class Config:
        """Pydantic configuration."""

        extra = Extra.allow
        allow_population_by_field_name = True
        alias_generator = to_camel_case

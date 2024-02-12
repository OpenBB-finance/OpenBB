"""The OpenBB Standardized QueryParams Model that holds the query input parameters."""

from typing import Dict

from pydantic import BaseModel, ConfigDict, model_validator

from openbb_core.provider.utils import validators


class QueryParams(BaseModel):
    """The OpenBB Standardized QueryParams Model that holds the query input parameters."""

    __alias_dict__: Dict[str, str] = {}
    __validator_dict__: Dict[str, tuple] = {}

    def __repr__(self):
        """Return the string representation of the QueryParams object."""
        return f"{self.__class__.__name__}({', '.join([f'{k}={v}' for k, v in self.model_dump().items()])})"

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def _apply_validators(cls, values):
        for v, fields in cls.__validator_dict__.items():
            for f in fields:
                func: validators.V
                if f in values and (func := getattr(validators, v)):
                    values[f] = func(f, values[f])
        return values

    def model_dump(self, *args, **kwargs):
        """Dump the model."""
        original = super().model_dump(*args, **kwargs)
        if self.__alias_dict__:
            return {
                self.__alias_dict__.get(key, key): value
                for key, value in original.items()
            }
        return original

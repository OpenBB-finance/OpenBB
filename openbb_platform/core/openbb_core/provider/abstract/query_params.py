"""The OpenBB Standardized QueryParams Model that holds the query input parameters."""

from typing import Dict, Optional, Tuple

from pydantic import BaseModel, ConfigDict, model_validator

from openbb_core.provider.utils import validators


class QueryParams(BaseModel):
    """The OpenBB Standardized QueryParams Model.

    The `QueryParams` class is designed to hold query parameters, to be extended by
    providers and to be used by fetchers when making data provider requests.

    Key Features:
    - Validators: The class applies a set of common validators if defined by the provider.
    - Alias handling: Utilizes an aliasing mechanism to maintain compatibility with different naming
        conventions across various data formats. The alias is only applied when running `model_dump`.

    Attributes:
    __validator_dict__ (Dict[str, tuple]):
        A dictionary that maps validator names to a tuple of fields where that validator
        should be applied. The validators must be defined in the validators.py module.
    __alias_dict__ (Dict[str, str]):
        A dictionary that maps field names to their aliases,
        facilitating the use of different naming conventions.
    model_config (ConfigDict):
        A configuration dictionary that defines the model's behavior,
        such as accepting extra fields, populating by name, and alias
        generation.
    """

    __alias_dict__: Dict[str, str] = {}
    __validator_dict__: Dict[str, Tuple[str]] = {}

    def __repr__(self):
        """Return the string representation of the QueryParams object."""
        return f"{self.__class__.__name__}({', '.join([f'{k}={v}' for k, v in self.model_dump().items()])})"

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def _apply_validators(cls, values):
        for v, fields in cls.__validator_dict__.items():
            for f in fields:
                func: Optional[validators.V]
                if f in values and (func := getattr(validators, v, None)):
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

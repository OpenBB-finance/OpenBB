"""The OpenBB Standardized Data Model."""

from typing import Dict

from pydantic import (
    AliasGenerator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    alias_generators,
    model_validator,
)
from typing_extensions import Annotated


def check_int(v: int) -> int:
    """Check if the value is an int."""
    try:
        return int(v)
    except ValueError as exc:
        raise TypeError("value must be an int") from exc


ForceInt = Annotated[int, BeforeValidator(check_int)]


class Data(BaseModel):
    """
    The OpenBB Standardized Data Model.

    The `Data` class is a flexible Pydantic model designed to accommodate various data structures
    for OpenBB's data processing pipeline as it's structured to support dynamic field definitions.

    The model leverages Pydantic's powerful validation features to ensure data integrity while
    providing the flexibility to handle extra fields that are not explicitly defined in the model's
    schema. This makes the `Data` class ideal for working with datasets that may have varying
    structures or come from heterogeneous sources.

    Key Features:
    - Dynamic field support: Can dynamically handle fields that are not pre-defined in the model,
        allowing for great flexibility in dealing with different data shapes.
    - Alias handling: Utilizes an aliasing mechanism to maintain compatibility with different naming
        conventions across various data formats.

    Usage:
    The `Data` class can be instantiated with keyword arguments corresponding to the fields of the
    expected data. It can also parse and validate data from JSON or other serializable formats, and
    convert them to a `Data` instance for easy manipulation and access.

    Example:
        # Direct instantiation
        data_record = Data(name="OpenBB", value=42)

        # Conversion from a dictionary
        data_dict = {"name": "OpenBB", "value": 42}
        data_record = Data(**data_dict)

    The class is highly extensible and can be subclassed to create more specific models tailored to
    particular datasets or domains, while still benefiting from the base functionality provided by the
    `Data` class.

    Attributes:
        __alias_dict__ (Dict[str, str]):
            A dictionary that maps field names to their aliases,
            facilitating the use of different naming conventions.
        model_config (ConfigDict):
            A configuration dictionary that defines the model's behavior,
            such as accepting extra fields, populating by name, and alias
            generation.
    """

    __alias_dict__: Dict[str, str] = {}

    def __repr__(self):
        """Return a string representation of the object."""
        return f"{self.__class__.__name__}({', '.join([f'{k}={v}' for k, v in super().model_dump().items()])})"

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        strict=False,
        alias_generator=AliasGenerator(
            validation_alias=alias_generators.to_camel,
            serialization_alias=alias_generators.to_snake,
        ),
    )

    @model_validator(mode="before")
    @classmethod
    def _use_alias(cls, values):
        """Use alias for error locs."""
        # set the alias dict values keys
        aliases = {orig: alias for alias, orig in cls.__alias_dict__.items()}
        if aliases and isinstance(values, dict):
            return {aliases.get(k, k): v for k, v in values.items()}

        return values

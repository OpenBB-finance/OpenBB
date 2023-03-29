from dataclasses import dataclass
from typing import Any, List, Optional

# pylint: disable=unidiomatic-typecheck


@dataclass(frozen=True)
class Parameter:
    """Class for storing parameters. This dataclass is frozen so no attributes can be changed after initialization.

    Parameters
    ----------
    name : str
        Name of the parameter.
    type_ : type
        Type of the parameter.
    default : Any
        Default value of the parameter.
    choices : Optional[List[Any]]
        List of possible values for the parameter.
    """

    name: str
    type_: Any
    default: Any
    choices: Optional[List[Any]] = None

    def __post_init__(self):
        """Post initialization."""
        self.validate()

    def validate(self):
        """Validate the value of the parameter.

        Parameters
        ----------
        value : Any
            Value of the parameter.

        Raises
        ------
        TypeError
            If the value is not of the correct type.
        ValueError
            If the value is not in the list of possible values.
        """
        if not self.validate_type(self.default):
            raise TypeError(
                f"Default for '{self.name}' must be of type '{self.type_.__name__}'."
            )
        if self.choices is not None and not all(
            self.validate_type(choice) for choice in self.choices
        ):
            raise TypeError(
                f"Choices must be of the same type as the parameter.\n"
                f"'{self.name}': '{self.choices}' -> '{self.type_.__name__}'"
            )
        if self.choices is not None and self.default not in self.choices:
            raise ValueError(
                f"Parameter '{self.name}' must be one of type '{self.choices}'."
            )

    def validate_type(self, value: Any) -> bool:
        """Check if the value is of the correct type.

        Parameters
        ----------
        value : Any
            Value of the parameter.

        Returns
        -------
        bool
            True if the value is of the correct type, False otherwise.
        """
        # Temporary workaround until we drop Python 3.9 for:
        # Error: Subscripted generics cannot be used with class and instance checks
        #
        # isinstance for subscripted generics (e.g. List[str]) is only available
        # in Python 3.10, so this method does not check for the type of subscripted generics.
        # TODO: Though we should implement it.
        # See https://stackoverflow.com/questions/70825351/python-3-typeerror-subscripted-generics-cannot-be-used-with-class-and-instance # noqa: E501
        try:
            return isinstance(value, self.type_)
        except Exception as _:  # noqa: F841
            return True

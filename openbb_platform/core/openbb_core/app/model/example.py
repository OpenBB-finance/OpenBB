"""Example class to represent endpoint examples."""

import datetime
from abc import abstractmethod
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    model_validator,
)

QUOTE_TYPES = {str, datetime.date}


class Example(BaseModel):
    """Example model."""

    scope: str

    model_config = ConfigDict(validate_assignment=True)

    @abstractmethod
    def to_python(self, **kwargs) -> str:
        """Return a Python code representation of the example."""

    @staticmethod
    def mock_ohlc_data() -> list:
        """Return mock data for the example."""
        # Pass number of observations as a parameter
        return [
            {
                "date": "2023-01-03",
                "open": 118.47,
                "high": 118.80,
                "low": 104.64,
                "close": 118.1,
                "volume": 231402800,
            },
            {
                "date": "2023-01-04",
                "open": 109.11,
                "high": 114.59,
                "low": 107.52,
                "close": 113.64,
                "volume": 180389000,
            },
            {
                "date": "2023-01-06",
                "open": 110.51,
                "high": 111.75,
                "low": 107.16,
                "close": 110.34,
                "volume": 157986300,
            },
            {
                "date": "2023-01-07",
                "open": 110.51,
                "high": 111.75,
                "low": 107.16,
                "close": 110.34,
                "volume": 157986300,
            },
            {
                "date": "2023-01-08",
                "open": 110.51,
                "high": 111.75,
                "low": 107.16,
                "close": 110.34,
                "volume": 157986300,
            },
            {
                "date": "2023-01-09",
                "open": 110.51,
                "high": 111.75,
                "low": 107.16,
                "close": 110.34,
                "volume": 157986300,
            },
            {
                "date": "2023-01-10",
                "open": 110.51,
                "high": 111.75,
                "low": 107.16,
                "close": 110.34,
                "volume": 157986300,
            },
            {
                "date": "2023-01-11",
                "open": 110.51,
                "high": 111.75,
                "low": 107.16,
                "close": 110.34,
                "volume": 157986300,
            },
        ]


class APIEx(Example):
    """API Example model."""

    scope: Literal["api"] = "api"
    description: Optional[str] = Field(
        default=None, description="Optional description unless more than 3 parameters"
    )
    parameters: Dict[str, Union[str, int, float, bool, List[Dict[str, Any]], None]]

    @computed_field  # type: ignore[misc]
    @property
    def provider(self) -> Optional[str]:
        """Return the provider from the parameters."""
        if provider := self.parameters.get("provider"):
            if isinstance(provider, str):
                return provider
            raise ValueError(f"Provider must be a string, not {type(provider)}")
        return None

    @model_validator(mode="before")
    @classmethod
    def check_model(cls, values: dict) -> dict:
        """Check if there are more than 3 parameters and a description is not added."""
        if len(values.get("parameters", {})) > 3 and not values.get("description"):
            raise ValueError(
                "API example with more than 3 parameters must have a description."
            )
        return values

    @staticmethod
    def unpack_type(type_: type) -> set:
        """Unpack types from types, example Union[List[str], int] -> {str, int}."""
        if hasattr(type_, "__args__"):
            return set().union(*map(APIEx.unpack_type, type_.__args__))
        return {type_} if isinstance(type_, type) else {type(type_)}

    def to_python(self, **kwargs) -> str:
        """Return a Python code representation of the example."""
        indentation = kwargs.get("indentation", "")
        func_path = kwargs.get("func_path", ".func_router.func_name")
        param_types: Dict[str, type] = kwargs.get("param_types", {})
        prompt = kwargs.get("prompt", "")

        eg = ""
        if self.description:
            eg += f"{indentation}{prompt}# {self.description}\n"

        eg += f"{indentation}{prompt}obb{func_path}("
        for k, v in self.parameters.items():
            if k in param_types and (type_ := param_types.get(k)):
                if QUOTE_TYPES.intersection(self.unpack_type(type_)):
                    eg += f"{k}='{v}', "
                else:
                    eg += f"{k}={v}, "
            else:
                eg += f"{k}={v}, "

        eg = indentation + eg.strip(", ") + ")\n"

        return eg


class PythonEx(Example):
    """Python Example model."""

    scope: Literal["python"] = "python"
    description: str
    code: List[str]

    def to_python(self, **kwargs) -> str:
        """Return a Python code representation of the example."""
        indentation = kwargs.get("indentation", "")
        prompt = kwargs.get("prompt", "")

        eg = ""
        if self.description:
            eg += f"{indentation}{prompt}# {self.description}\n"

        for line in self.code:
            eg += f"{indentation}{prompt}{line}\n"

        return eg


def filter_list(
    examples: List[Example],
    providers: List[str],
) -> List[Example]:
    """Filter list of examples."""
    return [
        e
        for e in examples
        if (isinstance(e, APIEx) and (not e.provider or e.provider in providers))
        or e.scope != "api"
    ]

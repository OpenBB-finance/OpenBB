"""Example class to represent endpoint examples."""

import datetime
from abc import abstractmethod
from typing import Any, Dict, List, Literal, Optional, Union, _UnionGenericAlias

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


class APIEx(Example):
    """API Example model."""

    scope: Literal["api"] = "api"
    description: Optional[str] = Field(
        default=None, description="Optional description unless more than 3 parameters"
    )
    parameters: Dict[
        str, Union[str, int, float, bool, List[str], List[Dict[str, Any]], None]
    ]

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
    def _unpack_type(type_: type) -> set:
        """Unpack types from types, example Union[List[str], int] -> {str, int}."""
        if (
            hasattr(type_, "__args__")
            and type(type_)  # pylint: disable=unidiomatic-typecheck
            is _UnionGenericAlias
        ):
            return set().union(*map(APIEx._unpack_type, type_.__args__))
        return {type_} if isinstance(type_, type) else {type(type_)}

    @staticmethod
    def _shift(i: int) -> float:
        """Return a transformation of the integer."""
        return 2 * (i + 1) / (2 * i) % 1 + 1

    @staticmethod
    def mock_data(
        dataset: Literal["timeseries", "panel"],
        size: int = 5,
        field_list: List[str] = None,
    ) -> List[Dict]:
        """Return mock data for the example.

        Parameters
        ----------
        dataset : str
            The type of data to return:
            - 'timeseries': Time series OHLC data
            - 'panel': Panel data asset manager (multiindex)

        size : int
            The size of the data to return, default is 5.
        field_list : List[str], optional
            The list of fields to return, default:
            - 'timeseries': ['close', 'volume']
            - 'panel': ['asset_manager', 'portfolio_value', 'risk_free_rate']

        Returns
        -------
        List[Dict]
            A list of dictionaries with the mock data.
        """
        if dataset == "timeseries":
            field_list = field_list or ["close", "volume"]
            assert len(field_list) == 2, "field_list must have 2 elements"
            result = []
            for i in range(1, size + 1):
                s = APIEx._shift(i)
                start_date = datetime.date(2023, 1, 1)
                result.append(
                    {
                        "date": (start_date + datetime.timedelta(days=i)).isoformat(),
                        field_list[0]: round(118.1 * s, 2),
                        field_list[1]: 231402800 + i * 1000000,
                    }
                )
            return result
        elif dataset == "panel":
            field_list = field_list or [
                "asset_manager",
                "portfolio_value",
                "risk_free_rate",
            ]
            assert len(field_list) == 3, "field_list must have 3 elements"
            result = []
            for i in range(1, size + 1):
                s = APIEx._shift(i)
                result.append(
                    {
                        field_list[0]: "BlackRock",
                        "time": i + 1,
                        field_list[1]: 100000 + i * 1000,
                        field_list[2]: round(0.02 * s, 2),
                        "is_multiindex": True,
                        "multiindex_names": "['asset_manager', 'time']",
                    }
                )
            return result
        raise ValueError(f"Dataset '{dataset}' not found.")

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
                if QUOTE_TYPES.intersection(self._unpack_type(type_)):
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

"""Example class to represent endpoint examples."""

from abc import abstractmethod
from dataclasses import Field
from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, computed_field, model_validator


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
    description: Optional[str] = None
    parameters: Dict[str, Union[str, int, float, bool, None]]

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
        if len(values.get("parameters", {})) > 3:
            raise ValueError(
                "API example has more than 3 parameters but doesn't have a description."
            )
        return values

    def to_python(self, **kwargs) -> str:
        """Return a Python code representation of the example."""
        indentation = kwargs.get("indentation", "")
        func_path = kwargs.get("func_path", ".func_router.func_name")
        func_params: Dict[str, Field] = kwargs.get("func_params", {})
        target: str = kwargs.get("target", "docstring")

        prompt = ">>> " if target == "docstring" else ""

        eg = ""
        if self.description:
            eg += f"{indentation}{prompt}# {self.description}\n"

        eg += f"{indentation}{prompt}obb{func_path}("
        for k, v in self.parameters.items():
            if k in func_params and (field := func_params.get(k)):
                field_type_str = str(field.type)
                if any(t in field_type_str for t in ["int", "float", "bool"]):
                    eg += f"{k}={v}, "
                else:
                    eg += f"{k}='{v}', "
            else:
                eg += f"{k}='{v}', "

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
        target: str = kwargs.get("target", "docstring")

        prompt = ">>> " if target == "docstring" else ""

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

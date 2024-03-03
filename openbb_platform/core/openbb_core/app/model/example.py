from dataclasses import Field
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, model_validator


class Example(BaseModel):
    """Example model."""

    scope: Literal["api", "python"] = "api"
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    code: Optional[List[str]] = None

    model_config = ConfigDict(validate_assignment=True)

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, values) -> dict:
        """Validate parameters and code based on scope."""
        # We could have used pydantic discriminators instead, but makes the code more
        # complex. We can revisit this in the future.
        scope = values.get("scope", "")
        parameters = values.get("parameters")
        code = values.get("code")

        if scope == "api" and not parameters:
            raise ValueError("Parameters are required for API examples.")
        if scope == "python" and not code:
            raise ValueError("Code is required for Python examples.")

        return values

    @property
    def provider(self) -> Optional[str]:
        """Return the provider from the parameters."""
        return self.parameters.get("provider") if self.parameters else None

    def to_python(
        self, func_name: str, func_params: Dict[str, Field], indentation: str = ""
    ) -> str:
        """Return a Python code representation of the example."""
        eg = ""
        if self.scope == "api" and self.parameters is not None:
            if self.description:
                eg += f"{indentation}>>> # {self.description}\n"
            eg += f"{indentation}>>> obb{func_name}("

            for k, v in self.parameters.items():
                if k in func_params and (field := func_params.get(k)):
                    field_type_str = str(field.type)
                    # TODO: Handle types better, some edge cases
                    # like Union[str, List[str]] will be stringified
                    # even if the type is a list
                    if any(t in field_type_str for t in ["int", "float", "bool"]):
                        eg += f"{k}={v}, "
                    else:
                        eg += f"{k}='{v}', "
                else:
                    eg += f"{k}='{v}', "

            eg = indentation + eg.strip(", ") + ")\n"
        elif self.scope == "python" and self.code is not None:
            for line in self.code:  # pylint: disable=not-an-iterable
                eg += f"{indentation}>>> {line}\n"

        return eg

    @staticmethod
    def filter_list(
        examples: List["Example"],
        providers: List[str],
    ) -> List["Example"]:
        """Filter list of examples."""
        return [
            e
            for e in examples
            if (e.scope == "api" and (not e.provider or e.provider in providers))
            or e.scope != "api"
        ]

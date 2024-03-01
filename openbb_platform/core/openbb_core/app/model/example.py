from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict
from dataclasses import Field


class Example(BaseModel):
    """Example model."""

    scope: Literal["api", "python"] = "api"
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    code: Optional[List[str]] = None

    model_config = ConfigDict(validate_assignment=True)

    def to_python(self, func_name: str, func_params: Dict[str, Field], indentation: str = "") -> str:
        """Return a Python code representation of the examplself."""
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
            eg += f"{indentation}>>> \n".join(self.code) + "\n"

        return eg

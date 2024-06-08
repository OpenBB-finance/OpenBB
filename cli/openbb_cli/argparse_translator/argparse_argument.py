"""Pydantic models for argparse arguments and argument groups."""

from typing import (
    Any,
    List,
    Literal,
    Optional,
    Tuple,
)

from pydantic import BaseModel, model_validator

SEP = "__"


class ArgparseArgumentModel(BaseModel):
    """Pydantic model for an argparse argument."""

    name: str
    type: Any
    dest: str
    default: Any
    required: bool
    action: Literal["store_true", "store"]
    help: Optional[str]
    nargs: Optional[Literal["+"]]
    choices: Optional[Tuple]

    @model_validator(mode="after")  # type: ignore
    @classmethod
    def validate_action(cls, values: "ArgparseArgumentModel"):
        """Validate the action based on the type."""
        if values.type is bool and values.action != "store_true":
            raise ValueError('If type is bool, action must be "store_true"')
        return values

    @model_validator(mode="after")  # type: ignore
    @classmethod
    def remove_props_on_store_true(cls, values: "ArgparseArgumentModel"):
        """Remove type, nargs, and choices if action is store_true."""
        if values.action == "store_true":
            values.type = None
            values.nargs = None
            values.choices = None
        return values

    # override
    def model_dump(self, **kwargs):
        """Override the model_dump method to remove empty choices."""
        res = super().model_dump(**kwargs)

        # Check if choices is present and if it's an empty tuple remove it
        if "choices" in res and not res["choices"]:
            del res["choices"]

        return res


class ArgparseArgumentGroupModel(BaseModel):
    """Pydantic model for a custom argument group."""

    name: str
    arguments: List[ArgparseArgumentModel]

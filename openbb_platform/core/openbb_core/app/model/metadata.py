"""Metadata model."""

from datetime import datetime
from typing import Any, Dict, Optional, Sequence, Union

from pydantic import BaseModel, Field, field_validator

from openbb_core.provider.abstract.data import Data


class Metadata(BaseModel):
    """Metadata of a command execution."""

    arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments of the command.",
    )
    duration: int = Field(
        description="Execution duration in nano second of the command."
    )
    route: str = Field(description="Route of the command.")
    timestamp: datetime = Field(description="Execution starting timestamp.")

    def __repr__(self) -> str:
        """Return string representation."""
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.model_dump().items()
        )

    @field_validator("arguments")
    @classmethod
    def scale_arguments(cls, v):
        """Scale arguments.

        This function is meant to limit the size of the input arguments of a command.
        If the type is one of the following: `Data`, `List[Data]`, `DataFrame`, `List[DataFrame]`,
        `Series`, `List[Series]` or `ndarray`, the value of the argument is swapped by a dictionary
        containing the type and the columns. If the type is not one of the previous, the
        value is kept or trimmed to 80 characters.
        """
        # pylint: disable=import-outside-toplevel
        from inspect import isclass  # noqa
        from numpy import ndarray  # noqa
        from pandas import DataFrame, Series  # noqa

        arguments: Dict[str, Any] = {}
        for item in ["provider_choices", "standard_params", "extra_params"]:
            arguments[item] = {}
            # The item could be class or it could a dictionary.
            v_item = (
                v.__dict__.get(item, {}) if not isinstance(v, dict) else v.get(item, {})
            )
            # The item might not be a dictionary yet.
            v_item = v_item if isinstance(v_item, dict) else v_item.__dict__
            for arg, arg_val in v_item.items():
                new_arg_val: Optional[Union[str, dict[str, Sequence[Any]]]] = None

                # Data
                if isclass(type(arg_val)) and issubclass(type(arg_val), Data):
                    new_arg_val = {
                        "type": f"{type(arg_val).__name__}",
                        "columns": list(arg_val.model_dump().keys()),
                    }

                # List[Data]
                if isinstance(arg_val, list) and issubclass(type(arg_val[0]), Data):
                    _columns = [list(d.model_dump().keys()) for d in arg_val]
                    ld_columns = (
                        item for sublist in _columns for item in sublist
                    )  # flatten
                    new_arg_val = {
                        "type": f"List[{type(arg_val[0]).__name__}]",
                        "columns": list(set(ld_columns)),
                    }

                # DataFrame
                elif isinstance(arg_val, DataFrame):
                    df_columns = (
                        list(arg_val.index.names) + arg_val.columns.tolist()
                        if any(index is not None for index in list(arg_val.index.names))
                        else arg_val.columns.tolist()
                    )
                    new_arg_val = {
                        "type": f"{type(arg_val).__name__}",
                        "columns": df_columns,
                    }

                # List[DataFrame]
                elif isinstance(arg_val, list) and issubclass(
                    type(arg_val[0]), DataFrame
                ):
                    ldf_columns = [
                        (
                            list(df.index.names) + df.columns.tolist()
                            if any(index is not None for index in list(df.index.names))
                            else df.columns.tolist()
                        )
                        for df in arg_val
                    ]
                    new_arg_val = {
                        "type": f"List[{type(arg_val[0]).__name__}]",
                        "columns": ldf_columns,
                    }

                # Series
                elif isinstance(arg_val, Series):
                    new_arg_val = {
                        "type": f"{type(arg_val).__name__}",
                        "columns": list(arg_val.index.names) + [arg_val.name],
                    }

                # List[Series]
                elif isinstance(arg_val, list) and isinstance(arg_val[0], Series):
                    ls_columns = [
                        (
                            list(series.index.names) + [series.name]
                            if any(
                                index is not None for index in list(series.index.names)
                            )
                            else series.name
                        )
                        for series in arg_val
                    ]
                    new_arg_val = {
                        "type": f"List[{type(arg_val[0]).__name__}]",
                        "columns": ls_columns,
                    }

                # ndarray
                elif isinstance(arg_val, ndarray):
                    new_arg_val = {
                        "type": f"{type(arg_val).__name__}",
                        "columns": list(arg_val.dtype.names or []),
                    }

                else:
                    str_repr_arg_val = str(arg_val)
                    if len(str_repr_arg_val) > 80:
                        new_arg_val = str_repr_arg_val[:80]

                arguments[item][arg] = new_arg_val or arg_val

        return arguments

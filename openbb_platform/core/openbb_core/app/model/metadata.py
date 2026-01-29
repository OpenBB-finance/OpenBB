"""元数据模型。"""

from collections.abc import Sequence
from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.data import Data
from pydantic import BaseModel, Field, field_validator


class Metadata(BaseModel):
    """命令执行的元数据。"""

    arguments: dict[str, Any] = Field(
        default_factory=dict,
        description="命令的参数。",
    )
    duration: int = Field(
        description="命令的执行持续时间（纳秒）。"
    )
    route: str = Field(description="命令的路由。")
    timestamp: datetime = Field(description="执行开始时间戳。")

    def __repr__(self) -> str:
        """返回字符串表示形式。"""
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.model_dump().items()
        )

    @field_validator("arguments")
    @classmethod
    def scale_arguments(cls, v):
        """缩放参数。

        此函数旨在限制命令输入参数的大小。
        如果类型是以下之一：`Data`、`List[Data]`、`DataFrame`、`List[DataFrame]`、
        `Series`、`List[Series]` 或 `ndarray`，则参数的值将替换为包含类型和列的字典。
        如果类型不是上述之一，则保留该值或将其修剪为 80 个字符。
        """
        # pylint: disable=import-outside-toplevel
        from inspect import isclass  # noqa
        from numpy import ndarray  # noqa
        from pandas import DataFrame, Series  # noqa

        arguments: dict[str, Any] = {}
        for item in ["provider_choices", "standard_params", "extra_params"]:
            arguments[item] = {}
            # 该项可以是类或字典。
            v_item = (
                v.__dict__.get(item, {}) if not isinstance(v, dict) else v.get(item, {})
            )
            # 该项可能还不是字典。
            v_item = v_item if isinstance(v_item, dict) else v_item.__dict__
            for arg, arg_val in v_item.items():
                new_arg_val: str | dict[str, Sequence[Any]] | None = None

                # Data 数据
                if isclass(type(arg_val)) and issubclass(type(arg_val), Data):
                    new_arg_val = {
                        "type": f"{type(arg_val).__name__}",
                        "columns": list(arg_val.model_dump().keys()),
                    }

                # List[Data] 数据列表
                if isinstance(arg_val, list) and issubclass(type(arg_val[0]), Data):
                    _columns = [list(d.model_dump().keys()) for d in arg_val]
                    ld_columns = (
                        item for sublist in _columns for item in sublist
                    )  # flatten
                    new_arg_val = {
                        "type": f"List[{type(arg_val[0]).__name__}]",
                        "columns": list(set(ld_columns)),
                    }

                # DataFrame 数据框
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

                # List[DataFrame] 数据框列表
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

                # Series 序列
                elif isinstance(arg_val, Series):
                    new_arg_val = {
                        "type": f"{type(arg_val).__name__}",
                        "columns": list(arg_val.index.names) + [arg_val.name],
                    }

                # List[Series] 序列列表
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

                # ndarray 多维数组
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

"""OpenBB Core 应用程序的实用函数。"""

import ast
import json
from datetime import time
from typing import TYPE_CHECKING, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.preferences import Preferences
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.provider.abstract.data import Data
from pydantic import ValidationError

if TYPE_CHECKING:
    # pylint: disable=import-outside-toplevel
    from numpy import ndarray
    from pandas import DataFrame, Series


def basemodel_to_df(
    data: list[Data] | Data,
    index: str | None = None,
) -> "DataFrame":
    """将 BaseModel 列表转换为 Pandas DataFrame。"""
    # pylint: disable=import-outside-toplevel
    from pandas import DataFrame, to_datetime

    if isinstance(data, list):
        df = DataFrame(
            [d.model_dump(exclude_none=True, exclude_unset=True) for d in data]
        )
    else:
        try:
            df = DataFrame(data.model_dump(exclude_none=True, exclude_unset=True))
        except ValueError:
            df = DataFrame(
                data.model_dump(exclude_none=True, exclude_unset=True), index=["values"]
            )

    if "is_multiindex" in df.columns:
        col_names = ast.literal_eval(df.multiindex_names.unique()[0])
        df = df.set_index(col_names)
        df = df.drop(["is_multiindex", "multiindex_names"], axis=1)

    # 如果日期列仅包含日期，则将其转换为日期以避免对时间数据进行编码。
    if "date" in df.columns:
        df["date"] = df["date"].apply(to_datetime)
        if all(t.time() == time(0, 0) for t in df["date"]):
            df["date"] = df["date"].apply(lambda x: x.date())

    if index and index in df.columns:
        if index == "date":
            df.set_index("date", inplace=True)
            df.sort_index(axis=0, inplace=True)
        else:
            df = df.set_index(index) if index and index in df.columns else df

    return df


def df_to_basemodel(
    df: Union["DataFrame", "Series"], index: bool = False
) -> list[Data]:
    """从 Pandas DataFrame 转换为 BaseModel 列表。"""
    # pylint: disable=import-outside-toplevel
    from pandas import MultiIndex, Series, to_datetime

    is_multiindex = isinstance(df.index, MultiIndex)

    if not is_multiindex and (index or df.index.name):
        df = df.reset_index()
    if isinstance(df, Series):
        df = df.to_frame()

    # 检查 df 是否具有 multiindex。如果是，则将索引名称添加到 df 和一个布尔列
    if isinstance(df.index, MultiIndex):
        df["is_multiindex"] = True
        df["multiindex_names"] = str(df.index.names)
        df = df.reset_index()

    # 转换为 JSON 将向所有没有时间元素的日期添加 T00:00:00.000，除非我们先将其格式化为字符串。
    if "date" in df.columns:
        df["date"] = df["date"].apply(to_datetime)
        if all(t.time() == time(0, 0) for t in df["date"]):
            df["date"] = df["date"].apply(lambda x: x.date().strftime("%Y-%m-%d"))

    return [
        Data(**d) for d in json.loads(df.to_json(orient="records", date_format="iso"))
    ]


def list_to_basemodel(data_list: list) -> list[Data]:
    """将列表转换为 BaseModel 列表。"""
    # pylint: disable=import-outside-toplevel
    from pandas import DataFrame, Series

    base_models = []
    for item in data_list:
        if isinstance(item, Data) or issubclass(type(item), Data):
            base_models.append(item)
        elif isinstance(item, dict):
            base_models.append(Data(**item))
        elif isinstance(item, (DataFrame, Series)):
            base_models.extend(df_to_basemodel(item))
        else:
            raise ValueError(f"不支持的列表项类型：{type(item)}")
    return base_models


def dict_to_basemodel(data_dict: dict) -> Data:
    """将字典转换为 BaseModel。"""
    try:
        return Data(**data_dict)
    except ValidationError as e:
        raise ValueError(
            f"将 dict 转换为 BaseModel 时发生验证错误：{e}"
        ) from e


def ndarray_to_basemodel(array: "ndarray") -> list[Data]:
    """将 NumPy 数组转换为 BaseModel 列表。"""
    # 假设一个 2D 数组，其中行是记录
    if array.ndim != 2:
        raise ValueError("仅支持 2D 数组。")
    return [
        Data(**{f"column_{i}": value for i, value in enumerate(row)}) for row in array
    ]


def convert_to_basemodel(data) -> Data | list[Data]:
    """将不同类型转换为 BaseModel 的分派函数。"""
    # pylint: disable=import-outside-toplevel
    from numpy import ndarray
    from pandas import DataFrame, Series

    if isinstance(data, Data) or issubclass(type(data), Data):
        return data
    if isinstance(data, list):
        return list_to_basemodel(data)
    if isinstance(data, dict):
        return dict_to_basemodel(data)
    if isinstance(data, (DataFrame, Series)):
        return df_to_basemodel(data)
    if isinstance(data, ndarray):
        return ndarray_to_basemodel(data)
    raise ValueError(f"不支持的数据类型：{type(data)}")


def get_target_column(df: "DataFrame", target: str) -> "Series":
    """从时间序列数据中获取目标列。"""
    if target not in df.columns:
        choices = ", ".join(df.columns)
        raise ValueError(
            f"在数据中未找到目标列 '{target}'。请从 {choices} 中选择"
        )
    return df[target]


def get_target_columns(df: "DataFrame", target_columns: list[str]) -> "DataFrame":
    """从时间序列数据中获取目标列。"""
    # pylint: disable=import-outside-toplevel
    from pandas import DataFrame

    df_result = DataFrame()
    for target in target_columns:
        df_result[target] = get_target_column(df, target).to_frame()
    return df_result


def get_user_cache_directory() -> str:
    """获取用户缓存目录。"""
    file = SystemSettings().model_dump()["user_settings_path"]

    with open(file) as settings_file:
        contents = settings_file.read()

    try:
        settings = json.loads(contents)["preferences"]
    except KeyError:
        settings = None
    cache_dir = (
        settings["cache_directory"]
        if settings and "cache_directory" in settings
        else Preferences().cache_directory
    )
    return cache_dir


def check_single_item(value: str | None, message: str | None = None) -> str | None:
    """检查字符串是否包含单个项目。"""
    if value and isinstance(value, str) and ("," in value or ";" in value):
        raise OpenBBError(message if message else "不允许多个项目")
    return value

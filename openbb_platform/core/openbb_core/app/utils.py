"""Utility functions for the OpenBB Core app."""

import ast
import json
from datetime import time
from typing import TYPE_CHECKING, Dict, List, Optional, Union

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
    data: Union[List[Data], Data],
    index: Optional[str] = None,
) -> "DataFrame":
    """Convert list of BaseModel to a Pandas DataFrame."""
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

    # If the date column contains dates only, convert them to a date to avoid encoding time data.
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
) -> List[Data]:
    """Convert from a Pandas DataFrame to list of BaseModel."""
    # pylint: disable=import-outside-toplevel
    from pandas import MultiIndex, Series, to_datetime

    is_multiindex = isinstance(df.index, MultiIndex)

    if not is_multiindex and (index or df.index.name):
        df = df.reset_index()
    if isinstance(df, Series):
        df = df.to_frame()

    # Check if df has multiindex.  If so, add the index names to the df and a boolean column
    if isinstance(df.index, MultiIndex):
        df["is_multiindex"] = True
        df["multiindex_names"] = str(df.index.names)
        df = df.reset_index()

    # Converting to JSON will add T00:00:00.000 to all dates with no time element unless we format it as a string first.
    if "date" in df.columns:
        df["date"] = df["date"].apply(to_datetime)
        if all(t.time() == time(0, 0) for t in df["date"]):
            df["date"] = df["date"].apply(lambda x: x.date().strftime("%Y-%m-%d"))

    return [
        Data(**d) for d in json.loads(df.to_json(orient="records", date_format="iso"))
    ]


def list_to_basemodel(data_list: List) -> List[Data]:
    """Convert a list to a list of BaseModel."""
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
            raise ValueError(f"Unsupported list item type: {type(item)}")
    return base_models


def dict_to_basemodel(data_dict: Dict) -> Data:
    """Convert a dictionary to BaseModel."""
    try:
        return Data(**data_dict)
    except ValidationError as e:
        raise ValueError(
            f"Validation error when converting dict to BaseModel: {e}"
        ) from e


def ndarray_to_basemodel(array: "ndarray") -> List[Data]:
    """Convert a NumPy array to list of BaseModel."""
    # Assuming a 2D array where rows are records
    if array.ndim != 2:
        raise ValueError("Only 2D arrays are supported.")
    return [
        Data(**{f"column_{i}": value for i, value in enumerate(row)}) for row in array
    ]


def convert_to_basemodel(data) -> Union[Data, List[Data]]:
    """Dispatch function to convert different types to BaseModel."""
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
    raise ValueError(f"Unsupported data type: {type(data)}")


def get_target_column(df: "DataFrame", target: str) -> "Series":
    """Get target column from time series data."""
    if target not in df.columns:
        choices = ", ".join(df.columns)
        raise ValueError(
            f"Target column '{target}' not found in data. Choose from {choices}"
        )
    return df[target]


def get_target_columns(df: "DataFrame", target_columns: List[str]) -> "DataFrame":
    """Get target columns from time series data."""
    # pylint: disable=import-outside-toplevel
    from pandas import DataFrame

    df_result = DataFrame()
    for target in target_columns:
        df_result[target] = get_target_column(df, target).to_frame()
    return df_result


def get_user_cache_directory() -> str:
    """Get user cache directory."""
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


def check_single_item(
    value: Optional[str], message: Optional[str] = None
) -> Optional[str]:
    """Check that string contains a single item."""
    if value and isinstance(value, str) and ("," in value or ";" in value):
        raise OpenBBError(message if message else "multiple items not allowed")
    return value

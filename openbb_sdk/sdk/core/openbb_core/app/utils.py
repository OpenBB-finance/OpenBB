import ast
from typing import Iterable, List, Optional, Union

import pandas as pd
from openbb_provider.abstract.data import Data


def basemodel_to_df(
    data: Union[List[Data], Data],
    index: Optional[Union[str, Iterable]] = None,
) -> pd.DataFrame:
    """Convert list of BaseModel to a Pandas DataFrame."""
    if isinstance(data, list):
        df = pd.DataFrame([d.dict() for d in data])
    else:
        try:
            df = pd.DataFrame(data.dict())
        except ValueError:
            df = pd.DataFrame(data.dict(), index=["values"])

    if "is_multiindex" in df.columns:
        col_names = ast.literal_eval(df.multiindex_names.unique()[0])
        df = df.set_index(col_names)
        df = df.drop(["is_multiindex", "multiindex_names"], axis=1)

    if index and index in df.columns:
        df = df.set_index(index)
        # TODO: This should probably check if the index can be converted to a datetime instead of just assuming
        if df.index.name == "date":
            df.index = pd.to_datetime(df.index)
            df.sort_index(axis=0, inplace=True)

    return df


def df_to_basemodel(
    df: Union[pd.DataFrame, pd.Series], index: bool = False
) -> List[Data]:
    """Convert from a Pandas DataFrame to list of BaseModel."""
    if index and not isinstance(df.index, pd.MultiIndex):
        df = df.reset_index(drop=True)
    if isinstance(df, pd.Series):
        df = df.to_frame()

    # Check if df has multiindex.  If so, add the index names to the df and a boolean column
    if isinstance(df.index, pd.MultiIndex):
        df["is_multiindex"] = True
        df["multiindex_names"] = str(df.index.names)
        df = df.reset_index()

    return [Data(**d) for d in df.to_dict(orient="records")]


def get_target_column(df: pd.DataFrame, target: str) -> pd.Series:
    """Get target column from time series data."""
    if target not in df.columns:
        choices = ", ".join(df.columns)
        raise ValueError(
            f"Target column '{target}' not found in data. Choose from {choices}"
        )
    return df[target]


def get_target_columns(df: pd.DataFrame, target_columns: List[str]) -> pd.DataFrame:
    df_result = pd.DataFrame()
    for target in target_columns:
        df_result[target] = get_target_column(df, target).to_frame()
    return df_result

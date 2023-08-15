from typing import List, Optional, Union

import pandas as pd
from openbb_provider.abstract.data import Data


def basemodel_to_df(
    data: Union[List[Data], Data], index: Optional[str] = None
) -> pd.DataFrame:
    """Convert list of BaseModel to a Pandas DataFrame."""

    if isinstance(data, list):
        df = pd.DataFrame([d.dict() for d in data])
    else:
        try:
            df = pd.DataFrame(data.dict())
        except ValueError:
            df = pd.DataFrame(data.dict(), index=["values"])

    if index and index in df.columns:
        df = df.set_index(index)
        if df.index.name == "date":
            df.index = pd.to_datetime(df.index)
            df.sort_index(axis=0, inplace=True)
    return df


def df_to_basemodel(
    df: Union[pd.DataFrame, pd.Series], index: bool = False
) -> List[Data]:
    """Convert from a Pandas DataFrame to list of BaseModel."""
    if index:
        df = df.reset_index()
    if isinstance(df, pd.Series):
        df = df.to_frame()
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

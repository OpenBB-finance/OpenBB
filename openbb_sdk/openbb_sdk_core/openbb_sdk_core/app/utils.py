from typing import List, Optional, Union

import pandas as pd
from pydantic import BaseModel


def to_dataframe(data: List[BaseModel], index: Optional[str] = None) -> pd.DataFrame:
    """Convert to a Pandas DataFrame."""
    df = pd.DataFrame([d.dict() for d in data])
    if index and index in df.columns:
        df = df.set_index(index)
    return df


def from_dataframe(
    df: Union[pd.DataFrame, pd.Series], index: bool = False
) -> List[BaseModel]:
    """Convert from a Pandas DataFrame."""
    if index:
        df = df.reset_index()
    if isinstance(df, pd.Series):
        df = df.to_frame()
    return [BaseModel(**d) for d in df.to_dict(orient="records")]


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

from typing import List, Optional, Union

import pandas as pd
from pydantic import BaseModel


def basemodel_to_df(data: List[BaseModel], index: Optional[str] = None) -> pd.DataFrame:
    """Convert to a Pandas DataFrame."""
    df = pd.DataFrame([d.dict() for d in data])
    if index and index in df.columns:
        df = df.set_index(index)
    return df


def df_to_basemodel(
    df: Union[pd.DataFrame, pd.Series], index: bool = False
) -> List[BaseModel]:
    """Convert from a Pandas DataFrame."""
    if index:
        df = df.reset_index()
    if isinstance(df, pd.Series):
        df = df.to_frame()
    return [BaseModel(**d) for d in df.to_dict(orient="records")]


# TODO: Move utils in common used in ta and qa to here

def get_target_column(*args, **kwargs):
    raise NotImplementedError

def get_target_columns(*args, **kwargs):
    raise NotImplementedError

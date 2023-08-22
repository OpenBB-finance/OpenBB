"""OpenBB filters."""

import pandas as pd

from openbb_core.app.utils import df_to_basemodel


def filter_inputs(**kwargs) -> dict:
    """Filter command inputs."""
    for key, value in kwargs.items():
        if isinstance(value, pd.DataFrame):
            kwargs[key] = df_to_basemodel(value, index=True)

    return kwargs

# pylint: disable=too-many-arguments
"""Probabilistic Exponential Smoothing Model"""
__docformat__ = "numpy"

import logging
from typing import List, Union

import numpy
import pandas as pd
from nixtlats import TimeGPT

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_KEY_NIXTLA"])
def get_timegpt_model(
    data: Union[pd.Series, pd.DataFrame],
    time_col: str = "ds",
    target_col: str = "y",
    forecast_horizon: int = 12,
    levels: List[float] = [80, 90],
    freq: Union[str, None] = None,
    finetune_steps: int = 0,
    clean_ex_first: bool = True,
    residuals: bool = False,
) -> pd.DataFrame:
    """TimeGPT was trained on the largest collection of data in history -
    over 100 billion rows of financial, weather, energy, and web data -
    and democratizes the power of time-series analysis.

    Parameters
    ----------
    data : Union[pd.Series, pd.DataFrame]
        Input data.
    time_col: str:
        Column that identifies each timestep, its values can be timestamps or integers. Defaults to "ds".
    target_column: str:
        Target column to forecast. Defaults to "y".
    forecast_horizon: int
        Number of days to forecast. Defaults to 12.
    levels: List[float]
        Confidence levels between 0 and 100 for prediction intervals.
    freq: Optional[str, None]
        Frequency of the data. By default, the freq will be inferred automatically.
    finetune_steps: int
        Number of steps used to finetune TimeGPT in the new data.
    clean_ex_first: bool
        Clean exogenous signal before making forecasts using TimeGPT.
    residuals: bool
        Whether to show residuals for the model. Defaults to False.

    Returns
    -------
    pd.DataFrame
        Forecasted values.
    """
    timegpt = TimeGPT(
        token=get_current_user().credentials.API_KEY_NIXTLA,
    )

    if isinstance(data[time_col].values[0], pd.Timestamp):
        data[time_col] = data[time_col].dt.strftime("%Y-%m-%d")
    elif isinstance(data[time_col].values[0], numpy.datetime64):
        data[time_col] = pd.to_datetime(data[time_col]).dt.strftime("%Y-%m-%d")

    fcst_df = timegpt.forecast(
        data,
        time_col=time_col,
        target_col=target_col,
        h=forecast_horizon,
        freq=freq,
        level=levels,
        finetune_steps=finetune_steps,
        clean_ex_first=clean_ex_first,
        add_history=residuals,
    )

    return fcst_df

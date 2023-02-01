# pylint: disable=too-many-arguments,E1101
"""Random Walk with Drift Model"""
__docformat__ = "numpy"

import logging
import warnings
from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from statsforecast.core import StatsForecast
from statsforecast.models import RandomWalkWithDrift

from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecast import helpers
from openbb_terminal.rich_config import console

warnings.simplefilter("ignore")

logger = logging.getLogger(__name__)

# pylint: disable=E1123


@log_start_end(log=logger)
def get_rwd_data(
    data: Union[pd.Series, pd.DataFrame],
    target_column: str = "close",
    n_predict: int = 5,
    start_window: float = 0.85,
    forecast_horizon: int = 5,
) -> Tuple[
    List[np.ndarray], List[np.ndarray], List[np.ndarray], Optional[float], StatsForecast
]:
    """Performs Random Walk with Drift forecasting
    This is a wrapper around StatsForecast RandomWalkWithDrift;
    we refer to this link for the original and more complete documentation of the parameters.


        https://nixtla.github.io/statsforecast/models.html#randomwalkwithdrift

    Parameters
    ----------
    data : Union[pd.Series, np.ndarray]
        Input data.
    target_column: Optional[str]:
        Target column to forecast. Defaults to "close".
    n_predict: int
        Number of days to forecast
    start_window: float
        Size of sliding window from start of timeseries and onwards
    forecast_horizon: int
        Number of days to forecast when backtesting and retraining historical

    Returns
    -------
    Tuple[List[np.ndarray], List[np.ndarray], List[np.ndarray], Optional[float], StatsForecast]:
        Adjusted Data series,
        List of historical fcast values,
        List of predicted fcast values,
        Optional[float] precision,
        Fit RWD model object.
    """

    use_scalers = False
    # statsforecast preprocessing
    # when including more time series
    # the preprocessing is similar
    _, ticker_series = helpers.get_series(data, target_column, is_scaler=use_scalers)
    freq = ticker_series.freq_str
    ticker_series = ticker_series.pd_dataframe().reset_index()
    ticker_series.columns = ["ds", "y"]
    ticker_series.insert(0, "unique_id", target_column)

    try:
        # Model Init
        model = RandomWalkWithDrift()
        fcst = StatsForecast(df=ticker_series, models=[model], freq=freq, verbose=True)
    except Exception as e:  # noqa
        error = str(e)
        if "got an unexpected keyword argument" in error:
            console.print(
                "[red]Please update statsforecast to version 1.1.3 or higher.[/red]"
            )
        else:
            console.print(f"[red]{error}[/red]")
        return [], [], [], None, None

    # Historical backtesting
    last_training_point = int((len(ticker_series) - 1) * start_window)
    historical_fcast = fcst.cross_validation(
        h=int(forecast_horizon),
        test_size=len(ticker_series) - last_training_point,
        n_windows=None,
        input_size=min(10 * forecast_horizon, len(ticker_series)),
    )

    # train new model on entire timeseries to provide best current forecast
    # we have the historical fcast, now lets predict.
    forecast = fcst.forecast(int(n_predict))
    y_true = historical_fcast["y"].values
    y_hat = historical_fcast["RWD"].values
    precision = helpers.mean_absolute_percentage_error(y_true, y_hat)
    console.print(f"RWD obtains MAPE: {precision:.2f}% \n")

    # transform outputs to make them compatible with
    # plots
    use_scalers = False
    _, ticker_series = helpers.get_series(
        ticker_series.rename(columns={"y": target_column}),
        target_column,
        is_scaler=use_scalers,
        time_col="ds",
    )
    _, forecast = helpers.get_series(
        forecast.rename(columns={"RWD": target_column}),
        target_column,
        is_scaler=use_scalers,
        time_col="ds",
    )
    _, historical_fcast = helpers.get_series(
        historical_fcast.groupby("ds").head(1).rename(columns={"RWD": target_column}),
        target_column,
        is_scaler=use_scalers,
        time_col="ds",
    )

    return (
        ticker_series,
        historical_fcast,
        forecast,
        float(precision),
        fcst,
    )

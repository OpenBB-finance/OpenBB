"""Theta Model"""
__docformat__ = "numpy"

import logging
import warnings
from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from darts import TimeSeries
from darts.metrics import mape, mse, rmse, smape
from darts.models import Theta
from darts.utils.utils import SeasonalityMode
from statsmodels.tools.sm_exceptions import ConvergenceWarning

from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecast import helpers
from openbb_terminal.rich_config import console

warnings.simplefilter("ignore", ConvergenceWarning)

SEASONS = ["N", "A", "M"]
PERIODS = [4, 5, 7]

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_theta_data(
    data: Union[pd.Series, pd.DataFrame],
    target_column: str = "close",
    seasonal: str = "M",
    seasonal_periods: int = 7,
    n_predict: int = 5,
    start_window: float = 0.85,
    forecast_horizon: int = 5,
    metric: str = "mape",
) -> Tuple[
    Optional[List[TimeSeries]],
    Optional[List[TimeSeries]],
    Optional[List[TimeSeries]],
    Optional[float],
    Optional[float],
    Optional[type[Theta]],
]:
    """Performs Theta forecasting
    An implementation of the 4Theta method with configurable theta parameter.

    https://unit8co.github.io/darts/generated_api/darts.models.forecasting.theta.html

    Parameters
    ----------
    data : Union[pd.Series, np.ndarray]
        Input data.
    target_column: Optional[str]:
        Target column to forecast. Defaults to "close".
    seasonal: str
        Seasonal component.  One of [N, A, M]
        Defaults to MULTIPLICATIVE.
    seasonal_periods: int
        Number of seasonal periods in a year
        If not set, inferred from frequency of the series.
    n_predict: int
        Number of days to forecast
    start_window: float
        Size of sliding window from start of timeseries and onwards
    forecast_horizon: int
        Number of days to forecast when backtesting and retraining historical data
    metric: str
        Metric to use when backtesting and retraining historical data. Defaults to "mape".

    Returns
    -------
    Tuple[List[TimeSeries], List[TimeSeries], List[TimeSeries], float, float, type[Theta]]
        Adjusted Data series,
        Historical forecast by best theta,
        list of Predictions,
        Mean average precision error,
        Best Theta,
        Theta Model.
    """

    use_scalers = False
    _, ticker_series = helpers.get_series(data, target_column, is_scaler=use_scalers)
    train, val = ticker_series.split_before(start_window)

    if seasonal == "A":
        seasonal = SeasonalityMode.ADDITIVE
    elif seasonal == "N":
        seasonal = SeasonalityMode.NONE
    else:  # Default
        seasonal = SeasonalityMode.MULTIPLICATIVE

    thetas = np.linspace(-10, 10, 50)
    best_mape = float("inf")
    best_theta = 0
    error = ""
    for theta in thetas:
        model = Theta(
            theta=theta,
            season_mode=seasonal,
            seasonality_period=seasonal_periods,
        )
        try:
            model.fit(train)
            pred_theta = model.predict(len(val))
            res = mape(val, pred_theta)
            if res < best_mape:
                best_mape = res
                best_theta = theta
        except Exception as e:  # noqa
            error = str(e)

    if best_theta == 0:
        console.print(f"[red]{error}[/red]")
        return [], [], [], 0, 0, None

    best_theta_model = Theta(
        best_theta,
        season_mode=seasonal,
        seasonality_period=seasonal_periods,
    )

    # Training model based on historical backtesting
    historical_fcast_theta = best_theta_model.historical_forecasts(
        ticker_series,
        start=float(start_window),
        forecast_horizon=int(forecast_horizon),
        verbose=True,
    )

    best_theta_model_final = Theta(
        best_theta,
        season_mode=seasonal,
        seasonality_period=seasonal_periods,
    )

    # fit model on entire series for final prediction
    best_theta_model_final.fit(ticker_series)
    prediction = best_theta_model_final.predict(int(n_predict))

    if metric == "rmse":
        precision = rmse(
            actual_series=ticker_series, pred_series=historical_fcast_theta
        )
    elif metric == "mse":
        precision = mse(actual_series=ticker_series, pred_series=historical_fcast_theta)
    elif metric == "mape":
        precision = mape(
            actual_series=ticker_series, pred_series=historical_fcast_theta
        )
    elif metric == "smape":
        precision = smape(
            actual_series=ticker_series, pred_series=historical_fcast_theta
        )

    console.print(f"Theta Model obtains {metric.upper()}: {precision:.2f}% \n")

    return (
        ticker_series,
        historical_fcast_theta,
        prediction,
        precision,
        best_theta,
        best_theta_model,
    )

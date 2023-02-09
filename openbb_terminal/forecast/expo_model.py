# pylint: disable=too-many-arguments
"""Probabilistic Exponential Smoothing Model"""
__docformat__ = "numpy"

import logging
import warnings
from typing import List, Optional, Tuple, Union

import pandas as pd
from darts import TimeSeries
from darts.metrics import mape, mse, rmse, smape
from darts.models import ExponentialSmoothing
from darts.utils.utils import ModelMode, SeasonalityMode
from numpy import ndarray
from statsmodels.tools.sm_exceptions import ConvergenceWarning

from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecast import helpers
from openbb_terminal.rich_config import console

warnings.simplefilter("ignore", ConvergenceWarning)


TRENDS = ["N", "A", "M"]
SEASONS = ["N", "A", "M"]
PERIODS = [4, 5, 7]
DAMPEN = ["T", "F"]

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_expo_data(
    data: Union[pd.Series, pd.DataFrame],
    target_column: str = "close",
    trend: str = "A",
    seasonal: str = "A",
    seasonal_periods: int = 7,
    dampen: str = "F",
    n_predict: int = 5,
    start_window: float = 0.85,
    forecast_horizon: int = 5,
    metric: str = "mape",
) -> Tuple[
    List[TimeSeries],
    List[TimeSeries],
    List[TimeSeries],
    Optional[Union[float, ndarray]],
    ExponentialSmoothing,
]:
    """Performs Probabilistic Exponential Smoothing forecasting
    This is a wrapper around statsmodels Holt-Winters' Exponential Smoothing;
    we refer to this link for the original and more complete documentation of the parameters.

    https://unit8co.github.io/darts/generated_api/darts.models.forecasting.exponential_smoothing.html

    Parameters
    ----------
    data : Union[pd.Series, np.ndarray]
        Input data.
    target_column: Optional[str]:
        Target column to forecast. Defaults to "close".
    trend: str
        Trend component.  One of [N, A, M]
        Defaults to ADDITIVE.
    seasonal: str
        Seasonal component.  One of [N, A, M]
        Defaults to ADDITIVE.
    seasonal_periods: int
        Number of seasonal periods in a year (7 for daily data)
        If not set, inferred from frequency of the series.
    dampen: str
        Dampen the function
    n_predict: int
        Number of days to forecast
    start_window: float
        Size of sliding window from start of timeseries and onwards
    forecast_horizon: int
        Number of days to forecast when backtesting and retraining historical
    metric: str
        Metric to use for backtesting. Defaults to MAPE.

    Returns
    -------
    Tuple[List[TimeSeries], List[TimeSeries], List[TimeSeries], Optional[Union[float, ndarray]], ExponentialSmoothing]
        Adjusted Data series,
        List of historical fcast values,
        List of predicted fcast values,
        Optional[float] - precision,
        Fit Prob. Expo model object.
    """

    use_scalers = False
    _, ticker_series = helpers.get_series(data, target_column, is_scaler=use_scalers)

    if trend == "M":
        trend_model = ModelMode.MULTIPLICATIVE
    elif trend == "N":
        trend_model = ModelMode.NONE
    else:  # Default
        trend_model = ModelMode.ADDITIVE

    if seasonal == "M":
        seasonal_model = SeasonalityMode.MULTIPLICATIVE
    elif seasonal == "N":
        seasonal_model = SeasonalityMode.NONE
    else:  # Default
        seasonal_model = SeasonalityMode.ADDITIVE

    damped = True
    if dampen == "F":
        damped = False

    # Model Init
    model_es = ExponentialSmoothing(
        trend=trend_model,
        seasonal=seasonal_model,
        seasonal_periods=int(seasonal_periods),
        damped=damped,
        random_state=42,
    )

    try:
        # Historical backtesting
        historical_fcast_es = model_es.historical_forecasts(
            ticker_series,  # backtest on entire ts
            start=float(start_window),
            forecast_horizon=int(forecast_horizon),
            verbose=True,
        )
    except Exception as e:  # noqa
        error = str(e)
        # lets translate this to something everyone understands
        if "with`overlap_end` set to `False`." in error:
            console.print(
                "[red]Dataset too small.[/red]"
                "[red] Please increase size to at least 100 data points.[/red]"
            )
        else:
            console.print(f"[red]{error}[/red]")
        return [], [], [], None, None

    # train new model on entire timeseries to provide best current forecast
    best_model = ExponentialSmoothing(
        trend=trend_model,
        seasonal=seasonal_model,
        seasonal_periods=int(seasonal_periods),
        damped=damped,
        random_state=42,
    )

    # we have the historical fcast, now lets train on entire set and predict.
    best_model.fit(ticker_series)
    probabilistic_forecast = best_model.predict(int(n_predict), num_samples=500)

    if metric == "rmse":
        precision = rmse(actual_series=ticker_series, pred_series=historical_fcast_es)
    elif metric == "mse":
        precision = mse(actual_series=ticker_series, pred_series=historical_fcast_es)
    elif metric == "mape":
        precision = mape(actual_series=ticker_series, pred_series=historical_fcast_es)
    elif metric == "smape":
        precision = smape(actual_series=ticker_series, pred_series=historical_fcast_es)

    console.print(
        f"Exponential smoothing obtains {metric.upper()}: {precision:.2f}% \n"
    )

    return (
        ticker_series,
        historical_fcast_es,
        probabilistic_forecast,
        precision,
        best_model,
    )

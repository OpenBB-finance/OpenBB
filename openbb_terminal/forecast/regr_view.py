""" Regression View"""
__docformat__ = "numpy"

import logging
from typing import Union, List, Optional
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt

from openbb_terminal.forecast import regr_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecast import helpers

logger = logging.getLogger(__name__)
# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def display_regression(
    data: Union[pd.Series, pd.DataFrame],
    target_column: str = "close",
    dataset_name: str = "",
    n_predict: int = 5,
    past_covariates: str = None,
    train_split: float = 0.85,
    forecast_horizon: int = 5,
    output_chunk_length: int = 5,
    lags: Union[int, List[int]] = 14,
    export: str = "",
    residuals: bool = False,
    forecast_only: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    naive: bool = False,
    explainability_raw: bool = False,
    export_pred_raw: bool = False,
    external_axes: Optional[List[plt.axes]] = None,
):
    """Display Regression Forecasting

    Parameters
    ----------
    data: Union[pd.Series, pd.DataFrame]
        Input Data
    target_column: str
        Target column to forecast. Defaults to "close".
    dataset_name: str
        The name of the ticker to be predicted
    n_predict: int
        Days to predict. Defaults to 5.
    train_split: float
        Train/val split. Defaults to 0.85.
    past_covariates: str
        Multiple secondary columns to factor in when forecasting. Defaults to None.
    forecast_horizon: int
        Forecast horizon when performing historical forecasting. Defaults to 5.
    output_chunk_length: int
        The length of the forecast of the model. Defaults to 1.
    lags: Union[int, List[int]]
        lagged target values to predict the next time step
    export: str
        Format to export data
    residuals: bool
        Whether to show residuals for the model. Defaults to False.
    forecast_only: bool
        Whether to only show dates in the forecasting range. Defaults to False.
    start_date: Optional[datetime]
        The starting date to perform analysis, data before this is trimmed. Defaults to None.
    end_date: Optional[datetime]
        The ending date to perform analysis, data after this is trimmed. Defaults to None.
    naive: bool
        Whether to show the naive baseline. This just assumes the closing price will be the same
        as the previous day's closing price. Defaults to False.
    external_axes: Optional[List[plt.axes]]
        External axes to plot on
    """
    data = helpers.clean_data(
        data, start_date, end_date, target_column, past_covariates
    )
    if not helpers.check_data(data, target_column, past_covariates):
        return
    output_chunk_length = helpers.check_output(
        output_chunk_length, n_predict, bool(past_covariates)
    )
    (
        ticker_series,
        historical_fcast,
        predicted_values,
        precision,
        _model,
    ) = regr_model.get_regression_data(
        data=data,
        n_predict=n_predict,
        target_column=target_column,
        past_covariates=past_covariates,
        train_split=train_split,
        forecast_horizon=forecast_horizon,
        output_chunk_length=output_chunk_length,
        lags=lags,
    )
    probabilistic = False
    helpers.plot_forecast(
        name="REGR",
        target_col=target_column,
        historical_fcast=historical_fcast,
        predicted_values=predicted_values,
        ticker_series=ticker_series,
        ticker_name=dataset_name,
        data=data,
        n_predict=n_predict,
        forecast_horizon=forecast_horizon,
        past_covariates=past_covariates,
        precision=precision,
        probabilistic=probabilistic,
        export=export,
        forecast_only=forecast_only,
        naive=naive,
        export_pred_raw=export_pred_raw,
        external_axes=external_axes,
    )
    if residuals:
        helpers.plot_residuals(
            _model, past_covariates, ticker_series, forecast_horizon=forecast_horizon
        )

    # SHAP
    helpers.plot_explainability(_model, explainability_raw)

# pylint: disable=too-many-arguments
"""Regression Model"""
__docformat__ = "numpy"

import logging
from typing import Any, Tuple, Union, List


import pandas as pd

from darts import TimeSeries
from darts.models import RegressionModel
from openbb_terminal.decorators import log_start_end

from openbb_terminal.forecasting import helpers

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_regression_data(
    data: Union[pd.Series, pd.DataFrame],
    n_predict: int = 5,
    target_col: str = "close",
    past_covariates: str = None,
    train_split: float = 0.85,
    forecast_horizon: int = 5,
    output_chunk_length: int = 1,
    lags: Union[int, List[int]] = 72,
) -> Tuple[List[TimeSeries], List[TimeSeries], List[TimeSeries], float, Any]:
    """Perform Regression Forecasting

    Args:
        data (Union[pd.Series, pd.DataFrame]):
            Input Data
        n_predict (int, optional):
            Days to predict. Defaults to 5.
        target_col (str, optional):
            Target column to forecast. Defaults to "close".
        train_split (float, optional):
            Train/val split. Defaults to 0.85.
        past_covariates (str, optional):
            Multiple secondary columns to factor in when forecasting. Defaults to None.
        forecast_horizon (int, optional):
            Forecast horizon when performing historical forecasting. Defaults to 5.
        output_chunk_length (int, optional):
            The length of the forecast of the model. Defaults to 1.
        lags (int, list)
            lagged target values to predict the next time step

    Returns:
        List[TimeSeries]
            Adjusted Data series
        List[TimeSeries]
            Historical forecast by best RNN model
        List[TimeSeries]
            list of Predictions
        float
            Mean average precision error
        Any
            Best NBEATS Model
    """
    # TODO add proper doc string
    # TODO Check if torch GPU AVAILABLE
    # TODO add in covariates
    # todo add in all possible parameters for training
    # Export model / save
    # load trained model
    filler, scaler, scaled_ticker_series = helpers.get_series(data, target_col)

    # scaled_train, scaled_val = scaled_ticker_series.split_before(float(train_split))

    scaled_past_covariate_whole, _, _ = helpers.scaled_past_covs(
        past_covariates, filler, data, train_split
    )

    lin_reg_model = RegressionModel(
        output_chunk_length=output_chunk_length, lags=lags, lags_past_covariates=lags
    )

    lin_reg_model.fit(scaled_ticker_series, scaled_past_covariate_whole)

    return helpers.get_prediction(
        scaler,
        past_covariates,
        lin_reg_model,
        scaled_ticker_series,
        scaled_past_covariate_whole,
        train_split,
        forecast_horizon,
        n_predict,
    )

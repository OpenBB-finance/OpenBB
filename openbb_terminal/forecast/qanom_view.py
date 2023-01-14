"""Quantile Anomaly Detector View"""
__docformat__ = "numpy"

import logging
from typing import Union, List, Optional
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt

from darts.ad import KMeansScorer
from darts.ad import QuantileDetector

#from openbb_terminal.forecast import qanomaly_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecast import helpers

logger = logging.getLogger(__name__)
# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def display_qanomaly_detection(
    data: Union[pd.Series, pd.DataFrame],
    target_column: str = "close",
    dataset_name: str = "",
    train_split: float = 0.85,
    forecast_horizon: int = 5,
    export: str = "",
    forecast_only: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    export_pred_raw: bool = False,
    external_axes: Optional[List[plt.axes]] = None,
):
    """Display Quantile Anomaly Detection

    Parameters
    ----------
    data: Union[pd.Series, pd.DataFrame]
        Input Data
    dataset_name: str
        The name of the ticker to be predicted
    n_predict: int
        Days to predict. Defaults to 5.
    target_col: str
        Target column to forecast. Defaults to "close".
    train_split: (float, optional)
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
        Whether to show the naive baseline. This just assumes the closing price will be the
        same as the previous day's closing price. Defaults to False.
    external_axes: Optional[List[plt.axes]]
        External axes to plot on
    """
    data = helpers.clean_data(
        data, start_date, end_date, target_column
    )
    if not helpers.check_data(data, target_column):
        return
    
    # split dataset into train and val
    train, val = data[:int(len(data) * train_split)], data[int(len(data) * train_split):]

    
    scorer = KMeansScorer(k=2, window=5)
    scorer.fit(train)
    anom_score = scorer.score(val)

    detector = QuantileDetector(high_quantile=0.99)
    detector.fit(scorer.score(train))
    binary_anom = detector.detect(anom_score)    

    data.plot()
    (anom_score / 2. - 100).plot(label="computed anomaly score", c="orangered", lw=3)
    (binary_anom * 45 - 150).plot(label="detected binary anomaly", lw=4)


    # (
    #     ticker_series,
    #     historical_fcast,
    #     predicted_values,
    #     precision,
    #     _model,
    # ) = linregr_model.get_linear_regression_data(
    #     data=data,
    #     n_predict=n_predict,
    #     target_column=target_column,
    #     past_covariates=past_covariates,
    #     train_split=train_split,
    #     forecast_horizon=forecast_horizon,
    #     output_chunk_length=output_chunk_length,
    #     lags=lags,
    # )

    # probabilistic = True
    # helpers.plot_forecast(
    #     name="LINREGR",
    #     target_col=target_column,
    #     historical_fcast=historical_fcast,
    #     predicted_values=predicted_values,
    #     ticker_series=ticker_series,
    #     ticker_name=dataset_name,
    #     data=data,
    #     n_predict=n_predict,
    #     forecast_horizon=forecast_horizon,
    #     past_covariates=past_covariates,
    #     precision=precision,
    #     probabilistic=probabilistic,
    #     export=export,
    #     forecast_only=forecast_only,
    #     naive=naive,
    #     export_pred_raw=export_pred_raw,
    #     external_axes=external_axes,
    # )


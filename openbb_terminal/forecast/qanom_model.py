# pylint: disable=too-many-arguments
"""Linear Regression Model"""
__docformat__ = "numpy"

import logging
from typing import Tuple, Union, List, Optional
import warnings

import matplotlib.pyplot as plt

import pandas as pd

from darts import TimeSeries
from darts.ad import KMeansScorer
from darts.ad import QuantileDetector
from openbb_terminal.decorators import log_start_end

from openbb_terminal.forecast import helpers

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_qanomaly_detection_data(
    data: Union[pd.Series, pd.DataFrame],
    target_column: str = "close",
    train_split: float = 0.85,
    forecast_horizon: int = 5,
    random_state: Optional[int] = None,
) -> Tuple[
    List[TimeSeries],
    # List[TimeSeries],
    # List[TimeSeries],
    # float,
]:
    """Perform Quantile Anomaly Detection

    Parameters
    ----------
    data: Union[pd.Series, pd.DataFrame]
        Input Data
    target_column: str
        Target column to forecast. Defaults to "close".
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
    random_state: Optional[int]
        The state for the model

    Returns
    -------
    Tuple[List[TimeSeries], List[TimeSeries], List[TimeSeries], float, LinearRegressionModel]
        Adjusted Data series,
        Historical forecast by best RNN model,
        list of Predictions,
        Mean average precision error,
        Best Linear Regression Model.
    """
    use_scalers = False
    probabilistic = False

    scaler, ticker_series = helpers.get_series(
        data, target_column, is_scaler=use_scalers
    )

    # split dataset into train and val
    train, val = ticker_series.split_before(train_split)

    scorer = KMeansScorer(k=2, window=5)
    scorer.fit(train)
    anom_score = scorer.score(val)

    detector = QuantileDetector(high_quantile=0.99)
    detector.fit(scorer.score(train))
    binary_anom = detector.detect(anom_score)    

    ticker_series.plot()
    (anom_score / 2. - 100).plot(label="computed anomaly score", c="orangered", lw=3)
    (binary_anom * 45 - 150).plot(label="detected binary anomaly", lw=4)
# pylint: disable=too-many-arguments
"""Quantile Anomaly Detection Model"""
__docformat__ = "numpy"

import logging
from typing import List, Tuple, Union

import pandas as pd
from darts import TimeSeries
from darts.ad import KMeansScorer, QuantileDetector

from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecast import helpers

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_anomaly_detection_data(
    data: Union[pd.Series, pd.DataFrame],
    target_column: str = "close",
    train_split: float = 0.6,
) -> Tuple[TimeSeries, List[TimeSeries], List[TimeSeries]]:
    """Get Quantile Anomaly Detection Data

    Parameters
    ----------
    data: Union[pd.Series, pd.DataFrame]

    Input Data
    -------
    target_column: str
        Target column to forecast. Defaults to "close".
    train_split: (float, optional)
        Train/val split. Defaults to 0.85.

    Returns
    -------
    Tuple[
        List[TimeSeries],
        List[TimeSeries],
        List[TimeSeries],
        ]
    """
    use_scalers = False

    _, ticker_series = helpers.get_series(data, target_column, is_scaler=use_scalers)

    # split dataset into train and val
    train, val = ticker_series.split_before(train_split)

    scorer = KMeansScorer(k=2, window=5)
    scorer.fit(train)
    anom_score = scorer.score(val)

    detector = QuantileDetector(high_quantile=0.99)
    detector.fit(scorer.score(train))
    binary_anom = detector.detect(anom_score)

    return ticker_series, anom_score, binary_anom

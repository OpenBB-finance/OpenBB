""" KNN Prediction View"""
__docformat__ = "numpy"

import logging
from typing import Union, Optional, List
from datetime import datetime

import pandas as pd
from matplotlib import pyplot as plt

from openbb_terminal.forecast import knn_model, helpers
from openbb_terminal.forecast.helpers import (
    print_pretty_prediction,
    plot_data_predictions,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

# pylint:disable=too-many-arguments


@log_start_end(log=logger)
def display_k_nearest_neighbors(
    data: Union[pd.DataFrame, pd.Series],
    target_column: str = "close",
    dataset_name: str = "",
    n_neighbors: int = 20,
    input_chunk_length: int = 14,
    n_predict: int = 5,
    test_size: float = 0.15,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    no_shuffle: bool = True,
    time_res: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display predictions using knn

    Parameters
    ----------
    data : Union[pd.DataFrame, pd.Series]
        Data to use for ML
    target_column: str, optional
        The column to select if a dataframe is sent
    dataset_name : str
        Stock data
    n_neighbors : int
        Number of neighbors for knn
    input_chunk_length : int
        Length of input sequences
    n_predict: int
        Number of days to predict
    test_size : float
        Fraction of data for testing
    start_date: Optional[datetime]
        The starting date to perform analysis, data before this is trimmed. Defaults to None.
    end_date: Optional[datetime]
        The ending date to perform analysis, data after this is trimmed. Defaults to None.
    no_shuffle : bool, optional
        Flag to shuffle data randomly, by default True
    time_res : str
        Resolution for data, allowing for predicting outside of standard market days
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    data = helpers.clean_data(data, start_date, end_date)
    if "date" in data.columns:
        data = data.set_index("date")
    if not helpers.check_data(data, target_column):
        return
    data = data[target_column]
    (
        forecast_data_df,
        preds,
        y_valid,
        y_dates_valid,
        scaler,
    ) = knn_model.get_knn_model_data(
        data=data,
        input_chunk_length=input_chunk_length,
        n_predict=n_predict,
        n_neighbors=n_neighbors,
        test_size=test_size,
        no_shuffle=no_shuffle,
    )

    if forecast_data_df.empty:
        console.print("Issue performing data prep and prediction")
        return

    if time_res:
        forecast_data_df.index = pd.date_range(
            data.index[-1], periods=n_predict + 1, freq=time_res
        )[1:]
    print_pretty_prediction(forecast_data_df[0], data.values[-1])
    plot_data_predictions(
        data=data,
        preds=preds,
        y_valid=y_valid,
        y_dates_valid=y_dates_valid,
        scaler=scaler,
        title=f"KNN Model with {n_neighbors} Neighbors on {dataset_name}",
        forecast_data=forecast_data_df,
        n_loops=1,
        time_str=time_res,
        external_axes=external_axes,
    )
    console.print("")

""" KNN Prediction View"""
__docformat__ = "numpy"

from typing import Union

import pandas as pd
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal.common.prediction_techniques.pred_helper import (
    print_pretty_prediction,
    plot_data_predictions,
)
from gamestonk_terminal.common.prediction_techniques import knn_model

register_matplotlib_converters()


def display_k_nearest_neighbors(
    ticker: str,
    data: Union[pd.DataFrame, pd.Series],
    n_neighbors: int,
    n_input_days: int,
    n_predict_days: int,
    test_size: float,
    end_date: str = "",
    no_shuffle: bool = True,
):
    """Display predictions using knn

    Parameters
    ----------
    ticker : str
        Stock data
    data : Union[pd.DataFrame, pd.Series]
        Data to use for ML
    n_neighbors : int
        Number of neighborns for knn
    n_input_days : int
        Length of input sequences
    n_predict_days : int
        Number of days to predict
    test_size : float
        Fraction of data for testing
    end_date : str, optional
        End date for backtesting, by default ""
    no_shuffle : bool, optional
        Flag to shuffle data randomly, by default True
    """
    (
        forecast_data_df,
        preds,
        y_valid,
        y_dates_valid,
        scaler,
    ) = knn_model.get_knn_model_data(
        data, n_input_days, n_predict_days, n_neighbors, test_size, end_date, no_shuffle
    )
    if forecast_data_df.empty:
        print("Issue performing data prep and prediction")
        return

    print_pretty_prediction(forecast_data_df[0], data.values[-1])
    plot_data_predictions(
        data,
        preds,
        y_valid,
        y_dates_valid,
        scaler,
        f"KNN Model with {n_neighbors} Neighbors on {ticker}",
        forecast_data_df,
        1,
    )
    print("")

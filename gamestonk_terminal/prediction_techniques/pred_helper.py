""" Prediction helper functions """
__docformat__ = "numpy"

import argparse
from typing import Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
from colorama import Fore, Style
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    mean_squared_error,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler, Normalizer
from gamestonk_terminal.helper_funcs import (
    get_next_stock_market_days,
    patch_pandas_text_adjustment,
    plot_autoscale,
)
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI

register_matplotlib_converters()


def prepare_scale_train_valid_test(
    df_stock: pd.DataFrame, ns_parser: argparse.Namespace
):
    """
    Prepare and scale train, validate and test data.
    Parameters
    ----------
    df_stock: pd.DataFrame
        Dataframe of stock prices
    ns_parser: argparse.Namespace
        Parsed arguments
    Returns
    -------
    X_train: np.ndarray
        Array of training data.  Shape (# samples, n_inputs, 1)
    X_test: np.ndarray
        Array of validation data.  Shape (#samples, n_inputs, 1)
    y_train: np.ndarray
        Array of training outputs.  Shape (#samples, n_days)
    y_test: np.ndarray
        Array of validation outputs.  Shape (#samples, n_days)
    X_dates_train: np.ndarray
        Array of dates for X_train
    X_dates_test: np.ndarray
        Array of dates for X_test
    y_dates_train: np.ndarray
        Array of dates for y_train
    y_dates_test: np.ndarray
        Array of dates for y)test
    test_data: np.ndarray
        Array of prices after the specified end date
    dates_test: np.ndarray
        Array of dates after specified end date
    scaler:
        Fitted preprocesser
    """
    parsed_end_date = ns_parser.s_end_date or df_stock.index[-1]-timedelta(days=3)
    n_input_days = ns_parser.n_inputs
    n_predict_days = ns_parser.n_days
    test_size = ns_parser.valid_split

    # Pre-process data
    if ns_parser.s_preprocessing == "standardization":
        scaler = StandardScaler()

    elif ns_parser.s_preprocessing == "minmax":
        scaler = MinMaxScaler()

    elif ns_parser.s_preprocessing == "normalization":
        scaler = Normalizer()

    test_data = df_stock[df_stock.index > parsed_end_date]
    train_data = df_stock[df_stock.index < parsed_end_date]
    dates = train_data.index
    dates_test = test_data.index
    scaler = scaler
    train_data = scaler.fit_transform(train_data.values.reshape(-1, 1))
    test_data = scaler.transform(test_data.values.reshape(-1, 1))
    prices = train_data

    input_dates = []
    input_prices = []
    next_n_day_prices = []
    next_n_day_dates = []

    for idx in range(len(prices) - n_input_days - n_predict_days):
        input_prices.append(prices[idx : idx + n_input_days])
        input_dates.append(dates[idx : idx + n_input_days])
        next_n_day_prices.append(
            prices[idx + n_input_days : idx + n_input_days + n_predict_days]
        )
        next_n_day_dates.append(
            dates[idx + n_input_days : idx + n_input_days + n_predict_days]
        )

    input_dates = np.asarray(input_dates)
    input_prices = np.array(input_prices)
    next_n_day_prices = np.array(next_n_day_prices)
    next_n_day_dates = np.asarray(next_n_day_dates)

    (
        X_train,
        X_test,
        y_train,
        y_test,
        X_dates_train,
        X_dates_test,
        y_dates_train,
        y_dates_test,
    ) = train_test_split(
        input_prices,
        next_n_day_prices,
        input_dates,
        next_n_day_dates,
        test_size=test_size,
    )
    return (
        X_train,
        X_test,
        y_train,
        y_test,
        X_dates_train,
        X_dates_test,
        y_dates_train,
        y_dates_test,
        test_data,
        dates_test,
        scaler,
    )


def get_backtesting_data(
    df_stock: pd.DataFrame, parsed_end_date: datetime, pred_days: int
) -> Tuple[pd.DataFrame, pd.DataFrame, bool]:
    """

    Parameters
    ----------
    df_stock: pd.DataFrame
        Dataframe of stock prices
    parsed_end_date: datetime
        Date that seperates test from prediction
    pred_days: int
        Number of days to predict

    Returns
    -------
    df_future: pd.DataFrame
        Dataframe of future prices
    df_stock: pd.DataFrame
        Dataframe of past prices
    Flag: bool
        Returns True if backtesting meets requirements, False if there are errors

    """
    if parsed_end_date < df_stock.index[0]:
        print(
            "Backtesting not allowed, since End Date is older than Start Date of historical data\n"
        )
        return pd.DataFrame(), pd.DataFrame(), False

    if (
        parsed_end_date
        < get_next_stock_market_days(
            last_stock_day=df_stock.index[0], n_next_days=5 + pred_days
        )[-1]
    ):
        print(
            "Backtesting not allowed, since End Date is too close to Start Date to train model\n"
        )
        return pd.DataFrame(), pd.DataFrame(), False

    future_index = get_next_stock_market_days(
        last_stock_day=parsed_end_date, n_next_days=pred_days
    )

    if future_index[-1] > datetime.now():
        print(
            "Backtesting not allowed, since End Date + Prediction days is in the future\n"
        )
        return pd.DataFrame(), pd.DataFrame(), False

    df_future = df_stock[future_index[0] : future_index[-1]]
    df_stock = df_stock[:parsed_end_date]
    return df_future, df_stock, True


def price_prediction_color(val: float, last_val: float) -> str:
    """Set prediction to be a colored string"""
    if float(val) > last_val:
        color = Fore.GREEN
    else:
        color = Fore.RED
    return f"{color}{val:.2f} ${Style.RESET_ALL}"


def print_pretty_prediction(df_pred: pd.DataFrame, last_price: float):
    """Print predictions"""
    if gtff.USE_COLOR:
        print(f"Actual price: {Fore.YELLOW}{last_price:.2f} ${Style.RESET_ALL}\n")
        print("Prediction:")
        print(df_pred.apply(price_prediction_color, last_val=last_price).to_string())
    else:
        print(f"Actual price: {last_price:.2f} $\n")
        print("Prediction:")
        print(df_pred.to_string())


def print_pretty_prediction_nn(df_pred: pd.DataFrame, last_price: float):
    if gtff.USE_COLOR:
        print(f"Actual price: {Fore.YELLOW}{last_price:.2f} ${Style.RESET_ALL}\n")
        print("Prediction:")
        print(
            df_pred.applymap(
                lambda x: price_prediction_color(x, last_val=last_price)
            ).to_string()
        )
    else:
        print(f"Actual price: {last_price:.2f} $\n")
        print("Prediction:")
        print(df_pred.to_string())


def mean_absolute_percentage_error(y_true: np.ndarray, y_pred: np.ndarray) -> np.number:
    """Calculate mean absolute percent error"""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def print_prediction_kpis(real: np.ndarray, pred: np.ndarray):
    """Print prediction statistics"""
    print("KPIs")
    print(f"MAPE: {mean_absolute_percentage_error(real, pred):.3f} %")
    print(f"R2: {r2_score(real, pred):.3f}")
    print(f"MAE: {mean_absolute_error(real, pred):.3f}")
    print(f"MSE: {mean_squared_error(real, pred):.3f}")
    print(f"RMSE: {mean_squared_error(real, pred, squared=False):.3f}")


def price_prediction_backtesting_color(val: list) -> str:
    """Add color to backtest data"""
    err_pct = 100 * (val[0] - val[1]) / val[1]
    if val[0] > val[1]:
        s_err_pct = f"       {Fore.GREEN} +{err_pct:.2f} %"
    else:
        s_err_pct = f"       {Fore.RED} {err_pct:.2f} %"
    return f"{val[1]:.2f}    x    {Fore.YELLOW}{val[0]:.2f}{s_err_pct}{Style.RESET_ALL}"

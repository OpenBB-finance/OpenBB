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

    # Test data is used for forcasting.  Takes the last n_input_days data points.
    # These points are not fed into training

    if ns_parser.s_end_date:
        df_stock = df_stock[df_stock.index <= ns_parser.s_end_date]
        if n_input_days + n_predict_days < df_stock.shape[0]:
            print("Cannot train enough input days to predict with loaded dataframe")
            return

    test_data = df_stock.iloc[-n_input_days:]
    train_data = df_stock.iloc[:-n_input_days]
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
        X_valid,
        y_train,
        y_valid,
        X_dates_train,
        X_dates_valid,
        y_dates_train,
        y_dates_valid,
    ) = train_test_split(
        input_prices,
        next_n_day_prices,
        input_dates,
        next_n_day_dates,
        test_size=test_size,
    )
    return (
        X_train,
        X_valid,
        y_train,
        y_valid,
        X_dates_train,
        X_dates_valid,
        y_dates_train,
        y_dates_valid,
        test_data,
        dates_test,
        scaler,
    )


def forecast(input_values, future_dates, model, scaler):

    future_values = scaler.inverse_transform(
        model.predict(input_values.reshape(1, -1, 1)).reshape(-1, 1)
    )
    df_future = pd.DataFrame(
        future_values, index=future_dates, columns=["Predicted Price"]
    )
    return df_future


def plot_data_predictions(
    df_stock, preds, y_valid, y_dates_valid, scaler, title, forecast_data
):

    plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
    plt.plot(
        df_stock.index,
        df_stock["5. adjusted close"].values,
        "-ob",
        lw=1,
        ms=2,
        label="Prices",
    )
    for i in range(len(y_valid) - 1):
        plt.plot(
            y_dates_valid[i],
            scaler.inverse_transform(preds[i].reshape(-1, 1)),
            "r",
            lw=3,
        )
        plt.fill_between(
            y_dates_valid[i],
            scaler.inverse_transform(preds[i].reshape(-1, 1)).ravel(),
            scaler.inverse_transform(y_valid[i].reshape(-1, 1)).ravel(),
            color="k",
            alpha=0.2,
        )
    plt.plot(
        y_dates_valid[-1],
        scaler.inverse_transform(preds[-1].reshape(-1, 1)),
        "r",
        lw=3,
        label="Predicions",
    )
    plt.fill_between(
        y_dates_valid[-1],
        scaler.inverse_transform(preds[-1].reshape(-1, 1)).ravel(),
        scaler.inverse_transform(y_valid[-1].reshape(-1, 1)).ravel(),
        color="k",
        alpha=0.2,
    )
    plt.axvspan(
        df_stock.index[-1], forecast_data.index[-1], facecolor="tab:orange", alpha=0.2
    )
    _, _, ymin, ymax = plt.axis()
    plt.vlines(
        df_stock.index[-1],
        ymin,
        ymax,
        colors="k",
        linewidth=3,
        linestyle="--",
        color="k",
    )
    plt.plot(forecast_data.index, forecast_data.values, "-ok", ms=5)
    plt.legend(loc=0)
    plt.xlim(df_stock.index[0], forecast_data.index[-1] + timedelta(days=1))
    plt.xlabel("Time")
    plt.ylabel("Share Price ($)")
    plt.grid(b=True, which="major", color="#666666", linestyle="-")
    plt.minorticks_on()
    plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    plt.title(title)
    if gtff.USE_ION:
        plt.ion()
    plt.show()
    print("")


def get_backtesting_data(
    df_stock: pd.DataFrame, parsed_end_date: datetime, pred_days: int
) -> Tuple[pd.DataFrame, pd.DataFrame, bool]:
    """

    Parameters
    ----------
    df_stock: pd.DataFrame
        Dataframe of stock prices
    parsed_end_date: datetime
        Date that separates test from prediction
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

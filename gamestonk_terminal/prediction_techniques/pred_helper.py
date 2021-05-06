""" Prediction helper functions """
__docformat__ = "numpy"

from typing import Tuple
from datetime import datetime
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

from gamestonk_terminal.helper_funcs import (
    get_next_stock_market_days,
    patch_pandas_text_adjustment,
    plot_autoscale,
)
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI

register_matplotlib_converters()


def prepare_train_valid_test(
    df_stock, parsed_end_date, n_input_days, n_predict_days, test_size
):

    df_test = df_stock[df_stock.index >= parsed_end_date]
    df_stock = df_stock[df_stock.index < parsed_end_date]
    dates = df_stock.index
    prices = df_stock["5. adjusted close"].values

    input_dates = []
    input_prices = []
    next_n_day_prices = []
    next_n_day_dates = []

    test_days = []
    test_inputs = []
    test_next_n_days = []

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
    input_prices = np.asarray(input_prices)
    next_n_day_prices = np.asarray(next_n_day_prices)
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


def plot_pred(
    df_stock: pd.DataFrame,
    df_future: pd.DataFrame,
    df_pred: pd.DataFrame,
    title: str,
    bt_flag: bool,
):
    plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
    plt.plot(df_stock.index, df_stock["5. adjusted close"], lw=2)
    plt.title(title)
    plt.xlim(df_stock.index[0], get_next_stock_market_days(df_pred.index[-1], 1)[-1])
    plt.xlabel("Time")
    plt.ylabel("Share Price ($)")
    plt.grid(b=True, which="major", color="#666666", linestyle="-")
    plt.minorticks_on()
    plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    df_ma = df_stock["5. adjusted close"].rolling(window=ns_parser.n_length).mean()
    plt.plot(df_ma.index, df_ma, lw=2, linestyle="--", c="tab:orange")
    plt.plot(
        [df_stock.index[-1], df_pred.index[0]],
        [df_stock["5. adjusted close"].values[-1], df_pred.values[0]],
        lw=1,
        c="tab:green",
        linestyle="--",
    )
    plt.plot(df_pred.index, df_pred, lw=2, c="tab:green")
    plt.axvspan(
        df_stock.index[-1], df_pred.index[-1], facecolor="tab:orange", alpha=0.2
    )
    _, _, ymin, ymax = plt.axis()
    plt.vlines(df_stock.index[-1], ymin, ymax, linewidth=1, linestyle="--", color="k")

    if bt_flag:
        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
        plt.subplot(211)
        plt.plot(
            df_future.index,
            df_future["5. adjusted close"],
            lw=2,
            c="tab:blue",
            ls="--",
        )
        plt.plot(df_pred.index, df_pred, lw=2, c="green")
        plt.scatter(df_future.index, df_future["5. adjusted close"], c="tab:blue", lw=3)
        plt.plot(
            [df_stock.index[-1], df_future.index[0]],
            [
                df_stock["5. adjusted close"].values[-1],
                df_future["5. adjusted close"].values[0],
            ],
            lw=2,
            c="tab:blue",
            ls="--",
        )
        plt.scatter(df_pred.index, df_pred, c="green", lw=3)
        plt.plot(
            [df_stock.index[-1], df_pred.index[0]],
            [df_stock["5. adjusted close"].values[-1], df_pred.values[0]],
            lw=2,
            c="green",
            ls="--",
        )
        plt.title("BACKTESTING: Real data price versus Prediction")
        plt.xlim(df_stock.index[-1], df_pred.index[-1] + datetime.timedelta(days=1))
        plt.xticks(
            [df_stock.index[-1], df_pred.index[-1] + datetime.timedelta(days=1)],
            visible=True,
        )
        plt.ylabel("Share Price ($)")
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        plt.legend(["Real data", "Prediction data"])
        plt.xticks([])

        plt.subplot(212)
        plt.axhline(y=0, color="k", linestyle="--", linewidth=2)
        plt.plot(
            df_future.index,
            100
            * (df_pred.values - df_future["5. adjusted close"].values)
            / df_future["5. adjusted close"].values,
            lw=2,
            c="red",
        )
        plt.scatter(
            df_future.index,
            100
            * (df_pred.values - df_future["5. adjusted close"].values)
            / df_future["5. adjusted close"].values,
            c="red",
            lw=5,
        )
        plt.title("BACKTESTING: Error between Real data and Prediction [%]")
        plt.plot(
            [df_stock.index[-1], df_future.index[0]],
            [
                0,
                100
                * (df_pred.values[0] - df_future["5. adjusted close"].values[0])
                / df_future["5. adjusted close"].values[0],
            ],
            lw=2,
            ls="--",
            c="red",
        )
        plt.xlim(df_stock.index[-1], df_pred.index[-1] + datetime.timedelta(days=1))
        plt.xticks(
            [df_stock.index[-1], df_pred.index[-1] + datetime.timedelta(days=1)],
            visible=True,
        )
        plt.xlabel("Time")
        plt.ylabel("Prediction Error (%)")
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        plt.legend(["Real data", "Prediction data"])

    if gtff.USE_ION:
        plt.ion()

    plt.show()

    pass


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

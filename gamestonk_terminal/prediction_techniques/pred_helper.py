""" Prediction helper functions """
__docformat__ = "numpy"

import argparse
from typing import List
import os
from warnings import simplefilter
from datetime import timedelta
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
from tensorflow.keras.models import Sequential
from gamestonk_terminal.helper_funcs import (
    check_positive,
    parse_known_args_and_warn,
    valid_date,
    plot_autoscale,
)
from gamestonk_terminal import config_neural_network_models as cfg
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI


register_matplotlib_converters()

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

simplefilter(action="ignore", category=FutureWarning)

# store the user's TensorFlow environment variables
ORIGINAL_TF_XLA_FLAGS = os.environ.get("TF_XLA_FLAGS")
ORIGINAL_TF_FORCE_GPU_ALLOW_GROWTH = os.environ.get("TF_FORCE_GPU_ALLOW_GROWTH")

PREPROCESSER = cfg.Preprocess


def check_valid_frac(num) -> float:
    if (num < 0) or (num > 1):
        raise argparse.ArgumentTypeError(f"{num} is an invalid percentage")
    return num


def restore_env():
    """Restore environment variables to original values"""

    def restore(key, value):
        if value is None:
            if key in os.environ:
                del os.environ[key]
        else:
            os.environ[key] = value

    restore("TF_XLA_FLAGS", ORIGINAL_TF_XLA_FLAGS)
    restore("TF_FORCE_GPU_ALLOW_GROWTH", ORIGINAL_TF_FORCE_GPU_ALLOW_GROWTH)


def parse_args(prog: str, description: str, other_args: List[str]):
    """
    Create an argparser and parse other_args. Will print help if user requests it.
    Parameters
    ----------
    prog: str
        Program for argparser
    description: str
        Description for argparser
    other_args
        Argparse arguments to pass
    Returns
    -------
    ns_parser: argparse.Namespace
        Parsed argument parser
    """

    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        add_help=False,
        formatter_class=argparse.RawTextHelpFormatter,  # enable multiline help messages
    )
    parser.add_argument(
        "-d",
        "--days",
        action="store",
        dest="n_days",
        type=check_positive,
        default=5,
        help="prediction days.",
    )
    parser.add_argument(
        "-i",
        "--input",
        action="store",
        dest="n_inputs",
        type=check_positive,
        default=40,
        help="number of days to use for prediction.",
    )
    parser.add_argument(
        "--epochs",
        action="store",
        dest="n_epochs",
        type=check_positive,
        default=50,
        help="number of training epochs.",
    )
    parser.add_argument(
        "-e",
        "--end",
        action="store",
        type=valid_date,
        dest="s_end_date",
        default=None,
        help="The end date (format YYYY-MM-DD) to select - Backtesting",
    )
    parser.add_argument(
        "--batch_size",
        action="store",
        dest="n_batch_size",
        type=check_positive,
        default=None,
        help="batch size for model fitting (use a power of 2)",
    )
    parser.add_argument(
        "--xla_cpu",
        action="store_true",
        dest="b_xla_cpu",
        default=False,
        help="enable XLA for CPU (see https://www.tensorflow.org/xla)",
    )
    parser.add_argument(
        "--xla_gpu",
        action="store_true",
        dest="b_xla_gpu",
        default=False,
        help="enable XLA for GPU (see https://www.tensorflow.org/xla)",
    )
    parser.add_argument(
        "--force_gpu_allow_growth",
        action="store",
        dest="s_force_gpu_allow_growth",
        default="true",
        choices=["true", "false", "default"],
        help="true: GPU memory will grow as needed. \n"
        "false: TensorFlow will allocate 100%% of GPU memory. \n"
        "default: usually the same as false, uses env/TensorFlow default",
    )
    parser.add_argument(
        "--loops",
        action="store",
        dest="n_loops",
        type=check_positive,
        default=1,
        help="number of loops to iterate and train models",
    )
    parser.add_argument(
        "-v",
        "--valid",
        type=check_valid_frac,
        dest="valid_split",
        default=0.1,
        help="Validation data split fraction",
    )

    parser.add_argument(
        "--lr",
        type=check_positive,
        dest="lr",
        default=0.01,
        help="Specify learning rate for optimizer.",
    )

    parser.add_argument(
        "--no_shuffle",
        action="store_false",
        dest="no_shuffle",
        default=True,
        help="Specify if shuffling validation inputs.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return None

        # set xla flags if requested
        xla_flags = (
            set(ORIGINAL_TF_XLA_FLAGS.split(" ")) if ORIGINAL_TF_XLA_FLAGS else set()
        )
        if ns_parser.b_xla_cpu or ns_parser.b_xla_gpu:
            xla_flags.add("--tf_xla_enable_xla_devices")
            if ns_parser.b_xla_cpu:
                xla_flags.add("--tf_xla_cpu_global_jit")
            if ns_parser.b_xla_gpu:
                xla_flags.add("--tf_xla_auto_jit=2")
        os.environ["TF_XLA_FLAGS"] = " ".join(xla_flags)

        # set GPU memory growth flag
        if ns_parser.s_force_gpu_allow_growth == "true":
            os.environ["TF_FORCE_GPU_ALLOW_GROWTH"] = "true"
        elif ns_parser.s_force_gpu_allow_growth == "false":
            os.environ["TF_FORCE_GPU_ALLOW_GROWTH"] = "false"

        return ns_parser

    except SystemExit:
        print("")
        return None


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
        Array of validation data.  Shape (totoal sequences - #samples, n_inputs, 1)
    y_train: np.ndarray
        Array of training outputs.  Shape (#samples, n_days)
    y_test: np.ndarray
        Array of validation outputs.  Shape (total sequences -#samples, n_days)
    X_dates_train: np.ndarray
        Array of dates for X_train
    X_dates_test: np.ndarray
        Array of dates for X_test
    y_dates_train: np.ndarray
        Array of dates for y_train
    y_dates_test: np.ndarray
        Array of dates for y_test
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
    if PREPROCESSER == "standardization":
        scaler = StandardScaler()

    elif PREPROCESSER == "minmax":
        scaler = MinMaxScaler()

    elif PREPROCESSER == "normalization":
        scaler = Normalizer()

    elif (PREPROCESSER == "none") or (PREPROCESSER is None):
        scaler = None
    # Test data is used for forecasting.  Takes the last n_input_days data points.
    # These points are not fed into training

    if ns_parser.s_end_date:
        df_stock = df_stock[df_stock.index <= ns_parser.s_end_date]
        if n_input_days + n_predict_days > df_stock.shape[0]:
            print("Cannot train enough input days to predict with loaded dataframe\n")
            return (
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                True,
            )

    test_data = df_stock.iloc[-n_input_days:]
    train_data = df_stock.iloc[:-n_input_days]

    dates = df_stock.index
    dates_test = test_data.index
    if scaler:
        train_data = scaler.fit_transform(df_stock.values.reshape(-1, 1))
        test_data = scaler.transform(test_data.values.reshape(-1, 1))
    else:
        train_data = df_stock.values.reshape(-1, 1)
        test_data = test_data.values.reshape(-1, 1)

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
        shuffle=ns_parser.no_shuffle,
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
        False,
    )


def forecast(
    input_values: np.ndarray, future_dates: List, model: Sequential, scaler
) -> pd.DataFrame:
    """
    Forecast the stock movement over future days and rescale
    Parameters
    ----------
    input_values: np.ndarray
        Array of values to be fed into the model
    future_dates: List
        List of future dates
    model: Sequential
        Pretrained model
    scaler:
        Fit scaler to be used to 'unscale' the data

    Returns
    -------
    df_future: pd.DataFrame
        Dataframe of predicted values
    """
    if scaler:
        future_values = scaler.inverse_transform(
            model.predict(input_values.reshape(1, -1, 1)).reshape(-1, 1)
        )
    else:
        future_values = model.predict(input_values.reshape(1, -1, 1)).reshape(-1, 1)

    df_future = pd.DataFrame(
        future_values, index=future_dates, columns=["Predicted Price"]
    )
    return df_future


def plot_data_predictions(
    df_stock, preds, y_valid, y_dates_valid, scaler, title, forecast_data, n_loops
):

    plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
    plt.plot(
        df_stock.index,
        df_stock["Adj Close"].values,
        "-ob",
        lw=1,
        ms=2,
        label="Prices",
    )
    for i in range(len(y_valid) - 1):

        if scaler:
            y_pred = scaler.inverse_transform(preds[i].reshape(-1, 1)).ravel()
            y_act = scaler.inverse_transform(y_valid[i].reshape(-1, 1)).ravel()
        else:
            y_pred = preds[i].ravel()
            y_act = y_valid[i].ravel()
        plt.plot(
            y_dates_valid[i],
            y_pred,
            "r",
            lw=1,
        )
        plt.fill_between(
            y_dates_valid[i],
            y_pred,
            y_act,
            where=(y_pred < y_act),
            color="r",
            alpha=0.2,
        )
        plt.fill_between(
            y_dates_valid[i],
            y_pred,
            y_act,
            where=(y_pred > y_act),
            color="g",
            alpha=0.2,
        )

    # Leave this one out of the loop so that the legend doesn't get overpopulated with "Predictions"
    if scaler:
        final_pred = scaler.inverse_transform(preds[-1].reshape(-1, 1)).ravel()
        final_valid = scaler.inverse_transform(y_valid[-1].reshape(-1, 1)).ravel()
    else:
        final_pred = preds[-1].reshape(-1, 1).ravel()
        final_valid = y_valid[-1].reshape(-1, 1).ravel()
    plt.plot(
        y_dates_valid[-1],
        final_pred,
        "r",
        lw=2,
        label="Predictions",
    )
    plt.fill_between(
        y_dates_valid[-1],
        final_pred,
        final_valid,
        color="k",
        alpha=0.2,
    )
    plt.axvspan(
        forecast_data.index[0] - timedelta(days=1),
        forecast_data.index[-1],
        facecolor="tab:orange",
        alpha=0.2,
    )
    _, _, ymin, ymax = plt.axis()
    plt.vlines(
        forecast_data.index[0] - timedelta(days=1),
        ymin,
        ymax,
        colors="k",
        linewidth=3,
        linestyle="--",
        color="k",
    )
    if n_loops == 1:
        plt.plot(
            forecast_data.index,
            forecast_data.values,
            "-ok",
            ms=3,
            label="Forecast",
        )
    else:
        plt.plot(
            forecast_data.index,
            forecast_data.median(axis=1).values,
            "-ok",
            ms=3,
            label="Forecast",
        )
        plt.fill_between(
            forecast_data.index,
            forecast_data.quantile(0.25, axis=1).values,
            forecast_data.quantile(0.75, axis=1).values,
            color="c",
            alpha=0.3,
        )
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

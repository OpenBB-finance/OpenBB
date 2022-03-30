""" Prediction helper functions """
__docformat__ = "numpy"

import argparse
from typing import List, Union, Optional
import os
import logging
from warnings import simplefilter
from datetime import timedelta
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    mean_squared_error,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler, Normalizer
from tensorflow.keras.models import Sequential
from openbb_terminal.helper_funcs import (
    check_positive,
    check_positive_float,
    parse_known_args_and_warn,
    valid_date,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal import config_neural_network_models as cfg
from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.rich_config import console
from openbb_terminal import rich_config

logger = logging.getLogger(__name__)

register_matplotlib_converters()

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

simplefilter(action="ignore", category=FutureWarning)

# store the user's TensorFlow environment variables
ORIGINAL_TF_XLA_FLAGS = os.environ.get("TF_XLA_FLAGS")
ORIGINAL_TF_FORCE_GPU_ALLOW_GROWTH = os.environ.get("TF_FORCE_GPU_ALLOW_GROWTH")

PREPROCESSOR = cfg.Preprocess


def check_valid_frac(num) -> float:
    """Argparse type checker for valid float between 0 and 1"""
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
        "-l",
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
        type=check_positive_float,
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
        console.print("")
        return None


def prepare_scale_train_valid_test(
    data: Union[pd.DataFrame, pd.Series],
    n_input_days: int,
    n_predict_days: int,
    test_size: float,
    s_end_date: str,
    no_shuffle: bool,
):
    """
    Prepare and scale train, validate and test data.
    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of stock prices
    ns_parser: argparse.Namespace
        Parsed arguments
    Returns
    -------
    X_train: np.ndarray
        Array of training data.  Shape (# samples, n_inputs, 1)
    X_test: np.ndarray
        Array of validation data.  Shape (total sequences - #samples, n_inputs, 1)
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
        Fitted PREPROCESSOR
    """

    # Pre-process data
    if PREPROCESSOR == "standardization":
        scaler = StandardScaler()

    elif PREPROCESSOR == "minmax":
        scaler = MinMaxScaler()

    elif PREPROCESSOR == "normalization":
        scaler = Normalizer()

    elif (PREPROCESSOR == "none") or (PREPROCESSOR is None):
        scaler = None
    # Test data is used for forecasting.  Takes the last n_input_days data points.
    # These points are not fed into training

    if s_end_date:
        data = data[data.index <= s_end_date]
        if n_input_days + n_predict_days > data.shape[0]:
            console.print(
                "Cannot train enough input days to predict with loaded dataframe\n"
            )
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

    test_data = data.iloc[-n_input_days:]
    train_data = data.iloc[:-n_input_days]

    dates = data.index
    dates_test = test_data.index
    if scaler:
        train_data = scaler.fit_transform(data.values.reshape(-1, 1))
        test_data = scaler.transform(test_data.values.reshape(-1, 1))
    else:
        train_data = data.values.reshape(-1, 1)
        test_data = test_data.values.reshape(-1, 1)

    prices = train_data

    input_dates = []
    input_prices = []
    next_n_day_prices = []
    next_n_day_dates = []

    for idx in range(len(prices) - n_input_days - n_predict_days):
        input_prices.append(prices[idx : idx + n_input_days])  # noqa: E203
        input_dates.append(dates[idx : idx + n_input_days])  # noqa: E203
        next_n_day_prices.append(
            prices[
                idx + n_input_days : idx + n_input_days + n_predict_days  # noqa: E203
            ]
        )
        next_n_day_dates.append(
            dates[
                idx + n_input_days : idx + n_input_days + n_predict_days  # noqa: E203
            ]
        )

    input_dates = np.asarray(input_dates)  # type: ignore
    input_prices = np.array(input_prices)  # type: ignore
    next_n_day_prices = np.array(next_n_day_prices)  # type: ignore
    next_n_day_dates = np.asarray(next_n_day_dates)  # type: ignore

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
        shuffle=no_shuffle,
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
        Fit scaler to be used to 'un-scale' the data

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


# pylint:disable=too-many-arguments


def plot_data_predictions(
    data,
    preds,
    y_valid,
    y_dates_valid,
    scaler,
    title,
    forecast_data,
    n_loops,
    time_str: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots data predictions for the different ML techniques
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item")
            console.print("[red]Expected list of 1 axis item./n[/red]")
            return
        (ax,) = external_axes

    ax.plot(
        data.index,
        data.values,
        "-o",
        ms=2,
        label="Real data",
    )
    for i in range(len(y_valid) - 1):

        if scaler:
            y_pred = scaler.inverse_transform(preds[i].reshape(-1, 1)).ravel()
            y_act = scaler.inverse_transform(y_valid[i].reshape(-1, 1)).ravel()
        else:
            y_pred = preds[i].ravel()
            y_act = y_valid[i].ravel()
        ax.plot(
            y_dates_valid[i],
            y_pred,
            color=theme.down_color,
        )
        ax.fill_between(
            y_dates_valid[i],
            y_pred,
            y_act,
            where=(y_pred < y_act),
            color=theme.down_color,
            alpha=0.2,
        )
        ax.fill_between(
            y_dates_valid[i],
            y_pred,
            y_act,
            where=(y_pred > y_act),
            color=theme.up_color,
            alpha=0.2,
        )

    # Leave this one out of the loop so that the legend doesn't get overpopulated with "Predictions"
    if scaler:
        final_pred = scaler.inverse_transform(preds[-1].reshape(-1, 1)).ravel()
        final_valid = scaler.inverse_transform(y_valid[-1].reshape(-1, 1)).ravel()
    else:
        final_pred = preds[-1].reshape(-1, 1).ravel()
        final_valid = y_valid[-1].reshape(-1, 1).ravel()
    ax.plot(
        y_dates_valid[-1],
        final_pred,
        color=theme.down_color,
        label="Predictions",
    )
    ax.fill_between(
        y_dates_valid[-1],
        final_pred,
        final_valid,
        alpha=0.2,
    )

    _, _, ymin, ymax = plt.axis()
    ax.vlines(
        forecast_data.index[0],
        ymin,
        ymax,
        linestyle="--",
    )
    if n_loops == 1:
        ax.plot(
            forecast_data.index,
            forecast_data.values,
            "-o",
            label="Forecast",
        )
    else:
        ax.plot(
            forecast_data.index,
            forecast_data.median(axis=1).values,
            "-o",
            label="Forecast",
        )
        ax.fill_between(
            forecast_data.index,
            forecast_data.quantile(0.25, axis=1).values,
            forecast_data.quantile(0.75, axis=1).values,
            alpha=0.3,
        )
    # Subtracting 1 day only works nicely for daily data.  For now if not daily, then start line on last point
    if not time_str or time_str == "1D":
        ax.axvspan(
            forecast_data.index[0] - timedelta(days=1),
            forecast_data.index[-1],
            alpha=0.2,
        )
        ax.set_xlim(data.index[0], forecast_data.index[-1] + timedelta(days=1))

    else:
        ax.axvspan(
            forecast_data.index[0],
            forecast_data.index[-1],
            alpha=0.2,
        )
        ax.set_xlim(data.index[0], forecast_data.index[-1])
    ax.set_title(title)
    ax.legend()
    ax.set_ylabel("Value")

    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()


def lambda_price_prediction_color(val: float, last_val: float) -> str:
    """Set prediction to be a colored string"""
    if float(val) > last_val:
        return f"[green]{val:.2f} $[/green]"
    return f"[red]{val:.2f} $[/red]"


def print_pretty_prediction(df_pred: pd.DataFrame, last_price: float):
    """Print predictions"""
    console.print("")
    if rich_config.USE_COLOR:
        df_pred = pd.DataFrame(df_pred)
        df_pred.columns = ["pred"]
        df_pred["pred"] = df_pred["pred"].apply(
            lambda x: lambda_price_prediction_color(x, last_val=last_price)
        )
        print_rich_table(
            df_pred,
            show_index=True,
            index_name="Datetime",
            headers=["Prediction"],
            floatfmt=".2f",
            title=f"Actual price: [yellow]{last_price:.2f} $[/yellow]\n",
        )

    else:
        df_pred = pd.DataFrame(df_pred)
        df_pred.columns = ["pred"]
        print_rich_table(
            df_pred,
            show_index=True,
            title=f"Actual price: [yellow]{last_price:.2f} $[/yellow]\n",
            index_name="Datetime",
            headers=["Prediction"],
            floatfmt=".2f",
        )


def print_pretty_prediction_nn(df_pred: pd.DataFrame, last_price: float):
    if rich_config.USE_COLOR:
        console.print(f"Actual price: [yellow]{last_price:.2f} $[/yellow]\n")
        console.print("Prediction:")
        console.print(
            df_pred.applymap(
                lambda x: lambda_price_prediction_color(x, last_val=last_price)
            ).to_string()
        )
    else:
        console.print(f"Actual price: {last_price:.2f} $\n")
        console.print("Prediction:")
        console.print(df_pred.to_string())


def mean_absolute_percentage_error(y_true: np.ndarray, y_pred: np.ndarray) -> np.number:
    """Calculate mean absolute percent error"""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def print_prediction_kpis(real: np.ndarray, pred: np.ndarray):
    """Print prediction statistics"""
    kpis = {
        "MAPE": f"{mean_absolute_percentage_error(real, pred) :.3f} %",
        "R2": f"{r2_score(real, pred) :.3f}",
        "MAE": f"{mean_absolute_error(real, pred):.3f}",
        "MSE": f"{mean_squared_error(real, pred):.3f}",
        "RMSE": f"{mean_squared_error(real, pred, squared=False):.3f}",
    }

    df = pd.DataFrame.from_dict(kpis, orient="index")
    print_rich_table(
        df,
        show_index=True,
        title="KPIs",
        floatfmt=".2f",
    )


def lambda_price_prediction_backtesting_color(val: list) -> str:
    """Add color to backtest data"""
    err_pct = 100 * (val[0] - val[1]) / val[1]
    if val[0] > val[1]:
        s_err_pct = f"       [green] +{err_pct:.2f} %"
        color = "[/green]"
    else:
        s_err_pct = f"       [red] {err_pct:.2f} %"
        color = "[/red]"
    return f"{val[1]:.2f}    x    [yellow]{val[0]:.2f}[/yellow]{s_err_pct}{color}"

""" Neural Networks View"""
__docformat__ = "numpy"

import argparse
from typing import List, Any, Union
import datetime
import os
import traceback
from warnings import simplefilter
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from TimeSeriesCrossValidation import splitTrain
from sklearn.preprocessing import MinMaxScaler, StandardScaler, Normalizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, SimpleRNN, Dense, Dropout

from gamestonk_terminal.helper_funcs import (
    check_positive,
    parse_known_args_and_warn,
    valid_date,
    patch_pandas_text_adjustment,
    get_next_stock_market_days,
    plot_autoscale,
)

from gamestonk_terminal.prediction_techniques.pred_helper import (
    print_pretty_prediction_nn,
    price_prediction_backtesting_color,
    print_prediction_kpis,
    prepare_scale_train_valid_test,
)

from gamestonk_terminal import feature_flags as gtff

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import config_neural_network_models as cfg_nn_models


register_matplotlib_converters()

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

simplefilter(action="ignore", category=FutureWarning)

# store the user's TensorFlow environment variables
ORIGINAL_TF_XLA_FLAGS = os.environ.get("TF_XLA_FLAGS")
ORIGINAL_TF_FORCE_GPU_ALLOW_GROWTH = os.environ.get("TF_FORCE_GPU_ALLOW_GROWTH")


def build_neural_network_model(
    Recurrent_Neural_Network: List[Any], n_inputs: int, n_days: int
):
    model = Sequential()

    for idx_layer, d_layer in enumerate(Recurrent_Neural_Network):
        # Recurrent Neural Network
        if str(*d_layer) == "SimpleRNN":
            # Is this the input layer? If so, define input_shape
            if idx_layer == 0:
                model.add(SimpleRNN(**d_layer["SimpleRNN"], input_shape=(n_inputs, 1)))
            # Is this the last output layer? If so, set units to prediction days
            elif idx_layer == (len(Recurrent_Neural_Network) - 1):
                model.add(SimpleRNN(**d_layer["SimpleRNN"], units=n_days))
            else:
                model.add(SimpleRNN(**d_layer["SimpleRNN"]))

        # Long-Short Term-Memory
        elif str(*d_layer) == "LSTM":
            # Is this the input layer? If so, define input_shape
            if idx_layer == 0:
                model.add(LSTM(**d_layer["LSTM"], input_shape=(n_inputs, 1)))
            # Is this the last output layer? If so, set units to prediction days
            elif idx_layer == (len(Recurrent_Neural_Network) - 1):
                model.add(LSTM(**d_layer["LSTM"], units=n_days))
            else:
                model.add(LSTM(**d_layer["LSTM"]))

        # Dense (Simple Neuron)
        elif str(*d_layer) == "Dense":
            # Is this the input layer? If so, define input_shape
            if idx_layer == 0:
                model.add(Dense(**d_layer["Dense"], input_dim=n_inputs))
            # Is this the last output layer? If so, set units to prediction days
            elif idx_layer == (len(Recurrent_Neural_Network) - 1):
                model.add(Dense(**d_layer["Dense"], units=n_days))
            else:
                model.add(Dense(**d_layer["Dense"]))

        # Dropout (Regularization)
        elif str(*d_layer) == "Dropout":
            model.add(Dropout(**d_layer["Dropout"]))

        else:
            print(f"Incorrect neuron type: {str(*d_layer)}")

    return model


def _parse_args(prog: str, description: str, other_args: List[str]):
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
        "-j",
        "--jumps",
        action="store",
        dest="n_jumps",
        type=check_positive,
        default=1,
        help="number of jumps in training data.",
    )
    parser.add_argument(
        "-p",
        "--pp",
        action="store",
        dest="s_preprocessing",
        default="minmax",
        choices=["normalization", "standardization", "minmax", "none"],
        help="pre-processing data.",
    )
    parser.add_argument(
        "-o",
        "--optimizer",
        action="store",
        dest="s_optimizer",
        default="adam",
        choices=[
            "adam",
            "adagrad",
            "adadelta",
            "adamax",
            "ftrl",
            "nadam",
            "rmsprop",
            "sgd",
        ],
        help="optimization technique (see https://www.tensorflow.org/api_docs/python/tf/keras/optimizers)",
    )
    parser.add_argument(
        "-l",
        "--loss",
        action="store",
        dest="s_loss",
        default="mae",
        choices=[
            "mae",
            "mape",
            "mse",
            "msle",
            "poisson",
            "logcosh",
            "kld",
            "hinge",
            "squared_hinge",
            "huber",
        ],
        help="loss function (see https://www.tensorflow.org/api_docs/python/tf/keras/losses)",
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
        type=float,
        dest="valid_split",
        default=0.1,
        help="Validation data split fraction",
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


def _restore_env():
    """Restore environment variables to original values"""

    def restore(key, value):
        if value is None:
            if key in os.environ:
                del os.environ[key]
        else:
            os.environ[key] = value

    restore("TF_XLA_FLAGS", ORIGINAL_TF_XLA_FLAGS)
    restore("TF_FORCE_GPU_ALLOW_GROWTH", ORIGINAL_TF_FORCE_GPU_ALLOW_GROWTH)


def _setup_backtesting(df_stock: pd.DataFrame, ns_parser: argparse.Namespace):
    """
    Setup backtesting when end data is specified
    Parameters
    ----------
    df_stock: pd.DataFrame
        Stock data
    ns_parser: argparse.Namespace
        Parsed arguments
    Returns
    -------
    df_stock: pd.DataFrame
        Data before end date
    df_future: pd.DataFrame
        Data after end date
    Raises
    -------
    Exception
        If configuration is invalid
    """

    df_future = None
    if ns_parser.s_end_date:
        if ns_parser.s_end_date < df_stock.index[0]:
            raise Exception(
                "Backtesting not allowed, since End Date is older than Start Date of historical data"
            )

        if ns_parser.s_end_date < get_next_stock_market_days(
            last_stock_day=df_stock.index[0],
            n_next_days=ns_parser.n_inputs + ns_parser.n_days,
        )[-1]:
            raise Exception(
                "Backtesting not allowed, since End Date is too close to Start Date to train model"
            )

        future_index = get_next_stock_market_days(
            last_stock_day=ns_parser.s_end_date, n_next_days=ns_parser.n_days
        )

        if future_index[-1] > datetime.datetime.now():
            raise Exception(
                "Backtesting not allowed, since End Date + Prediction days is in the future"
            )

        df_future = df_stock[future_index[0] : future_index[-1]]
        df_stock = df_stock[: ns_parser.s_end_date]
    return df_stock, df_future


def _preprocess_split(df_stock: pd.DataFrame, ns_parser: argparse.Namespace):
    """
    Preprocess and split dstock data
    Parameters
    ----------
    df_stock: pd.DataFrame
        Dataframe of stock prices
    ns_parser: argparse.Namespace
        Parsed argparse arguments

    Returns
    -------
    scaler: Union[MinMaxScaler, StandardScaler, Normalizer]
        sklearn scaler used
    stock_train_data: np.ndarray
        All training data
    stock_x: np.ndarray
        Inputs for model
    stock_y: np.ndarray
        Outputs for model
    Raises
    -------
    Exception
        Not enough training data is provided
    """

    # Pre-process data
    if ns_parser.s_preprocessing == "standardization":
        scaler = StandardScaler()
        stock_train_data = scaler.fit_transform(
            np.array(df_stock["5. adjusted close"].values.reshape(-1, 1))
        )
    elif ns_parser.s_preprocessing == "minmax":
        scaler = MinMaxScaler()
        stock_train_data = scaler.fit_transform(
            np.array(df_stock["5. adjusted close"].values.reshape(-1, 1))
        )
    elif ns_parser.s_preprocessing == "normalization":
        scaler = Normalizer()
        stock_train_data = scaler.fit_transform(
            np.array(df_stock["5. adjusted close"].values.reshape(-1, 1))
        )
    else:  # No pre-processing
        stock_train_data = np.array(df_stock["5. adjusted close"].values.reshape(-1, 1))

    # Split training data for the neural network
    stock_x, stock_y = splitTrain.split_train(
        stock_train_data,
        ns_parser.n_inputs,
        ns_parser.n_days,
        numJumps=ns_parser.n_jumps,
    )
    if not stock_x:
        raise Exception("Given the model parameters more training data is needed.")

    stock_x = np.array(stock_x)
    stock_y = np.array(stock_y)

    return scaler, stock_train_data, stock_x, stock_y


def _rescale_data(
    df_stock: pd.DataFrame,
    ns_parser: argparse.Namespace,
    scaler: Union[MinMaxScaler, StandardScaler, Normalizer],
    yhat: np.ndarray,
    idx_loop: int,
):
    """
    Re-scale the data back and return the prediction dataframe.
    Parameters
    ----------
    df_stock: pd.DataFrame
        Dataframe of stock prices
    ns_parser: argparse.Namespace
        Parsed argument parser
    scaler:
        One of the predefined sklearn scalers
    yhat: np.ndarry
        Predicted values
    idx_loop: int
        Loop index

    Returns
    -------
    df_pred: pd.Series
        Series of resclaled predictions
    """
    if (
        (ns_parser.s_preprocessing == "standardization")
        or (ns_parser.s_preprocessing == "normalization")
        or (ns_parser.s_preprocessing == "minmax")
    ):
        y_pred_test_t = scaler.inverse_transform(yhat.tolist())
    else:
        y_pred_test_t = yhat

    l_pred_days = get_next_stock_market_days(
        last_stock_day=df_stock["5. adjusted close"].index[-1],
        n_next_days=ns_parser.n_days,
    )
    column_name = f"Price [{idx_loop+1}]"
    df_pred = pd.Series(y_pred_test_t[0].tolist(), index=l_pred_days, name=column_name)
    return df_pred


def _plot_and_print_results(
    df_stock: pd.DataFrame,
    ns_parser: argparse.Namespace,
    df_future: pd.DataFrame,
    df_pred: pd.DataFrame,
    model_name: str,
    s_ticker: str,
):
    """
    Plot and print results
    Parameters
    ----------
    df_stock: pd.DataFrame:
        Dataframe of stock prices
    ns_parser: argparse.Namespace
        Parsed argument parser
    df_future: pd.DataFrame
        Dataframe of future prices
    df_pred: pd.DataFrame
        Dataframe of predicted prices
    model_name: str
        Model Name
    s_ticker: str
        Ticker

    Returns
    -------

    """

    # Plotting
    plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
    plt.plot(df_stock.index, df_stock["5. adjusted close"], lw=3)

    # BACKTESTING
    if ns_parser.n_loops == 1:
        if ns_parser.s_end_date:
            plt.title(
                f"BACKTESTING: {model_name} on {s_ticker} - {ns_parser.n_days} days prediction"
            )
        else:
            plt.title(
                f"{model_name} on {s_ticker} - {ns_parser.n_days} days prediction"
            )
    else:
        if ns_parser.s_end_date:
            plt.title(
                f"{ns_parser.n_loops} loops - BACKTESTING: {model_name} on {s_ticker}"
                f" - {ns_parser.n_days} days prediction"
            )
        else:
            plt.title(
                f"{ns_parser.n_loops} loops - {model_name} on {s_ticker} - {ns_parser.n_days} days prediction"
            )

    plt.xlim(df_stock.index[0], get_next_stock_market_days(df_pred.index[-1], 1)[-1])
    plt.xlabel("Time")
    plt.ylabel("Share Price ($)")
    plt.grid(b=True, which="major", color="#666666", linestyle="-")
    plt.minorticks_on()
    plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

    if ns_parser.n_loops == 1:
        plt.plot(
            [df_stock.index[-1], df_pred.index[0]],
            [
                df_stock["5. adjusted close"].values[-1],
                df_pred[df_pred.columns[0]].values[0],
            ],
            lw=1,
            c="tab:green",
            linestyle="--",
        )
        plt.plot(df_pred.index, df_pred[df_pred.columns[0]], lw=2, c="tab:green")
    else:
        df_quantiles = pd.DataFrame()
        df_quantiles["Quantile 10%"] = df_pred.quantile(0.1, axis=1)
        df_quantiles["Median"] = df_pred.quantile(0.5, axis=1)
        df_quantiles["Quantile 90%"] = df_pred.quantile(0.9, axis=1)

        plt.plot(df_pred.index, df_quantiles["Median"], lw=2, c="tab:green")
        plt.fill_between(
            df_pred.index,
            df_quantiles["Quantile 10%"],
            df_quantiles["Quantile 90%"],
            alpha=0.30,
            color="tab:green",
            interpolate=True,
        )
        plt.fill_between(
            [df_stock.index[-1], df_pred.index[0]],
            [
                df_stock["5. adjusted close"].values[-1],
                df_quantiles["Quantile 10%"].values[0],
            ],
            [
                df_stock["5. adjusted close"].values[-1],
                df_quantiles["Quantile 90%"].values[0],
            ],
            alpha=0.30,
            color="tab:green",
            interpolate=True,
        )

    plt.axvspan(
        df_stock.index[-1], df_pred.index[-1], facecolor="tab:orange", alpha=0.2
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

    # BACKTESTING
    if ns_parser.s_end_date:
        plt.plot(
            df_future.index,
            df_future["5. adjusted close"],
            lw=2,
            c="tab:blue",
            ls="--",
        )
        plt.plot(
            [df_stock.index[-1], df_future.index[0]],
            [
                df_stock["5. adjusted close"].values[-1],
                df_future["5. adjusted close"].values[0],
            ],
            lw=1,
            c="tab:blue",
            linestyle="--",
        )

    if gtff.USE_ION:
        plt.ion()

    plt.show()

    # BACKTESTING
    if ns_parser.s_end_date:
        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
        plt.subplot(211)
        plt.plot(
            df_future.index,
            df_future["5. adjusted close"],
            lw=2,
            c="tab:blue",
            ls="--",
        )
        if ns_parser.n_loops == 1:
            plt.plot(df_pred.index, df_pred, lw=2, c="green")
        else:
            plt.plot(
                df_quantiles["Median"].index, df_quantiles["Median"], lw=2, c="green"
            )

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
        if ns_parser.n_loops == 1:
            plt.scatter(df_pred.index, df_pred, c="green", lw=3)
            plt.plot(
                [df_stock.index[-1], df_pred.index[0]],
                [df_stock["5. adjusted close"].values[-1], df_pred.values[0]],
                lw=2,
                c="green",
                ls="--",
            )
        else:
            plt.scatter(
                df_quantiles["Median"].index, df_quantiles["Median"], lw=3, c="green"
            )
            plt.plot(
                [df_stock.index[-1], df_quantiles["Median"].index[0]],
                [
                    df_stock["5. adjusted close"].values[-1],
                    df_quantiles["Median"].values[0],
                ],
                lw=2,
                c="green",
                ls="--",
            )
            plt.fill_between(
                df_pred.index,
                df_quantiles["Quantile 10%"],
                df_quantiles["Quantile 90%"],
                alpha=0.30,
                color="tab:green",
                interpolate=True,
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
        if ns_parser.n_loops == 1:
            plt.plot(
                df_future.index,
                100
                * (
                    df_pred[df_pred.columns[0]].values
                    - df_future["5. adjusted close"].values
                )
                / df_future["5. adjusted close"].values,
                lw=2,
                c="red",
            )
            plt.scatter(
                df_future.index,
                100
                * (
                    df_pred[df_pred.columns[0]].values
                    - df_future["5. adjusted close"].values
                )
                / df_future["5. adjusted close"].values,
                c="red",
                lw=5,
            )
            plt.plot(
                [df_stock.index[-1], df_future.index[0]],
                [
                    0,
                    100
                    * (
                        df_pred[df_pred.columns[0]].values[0]
                        - df_future["5. adjusted close"].values[0]
                    )
                    / df_future["5. adjusted close"].values[0],
                ],
                lw=2,
                ls="--",
                c="red",
            )
        else:
            plt.plot(
                df_future.index,
                100
                * (
                    df_quantiles["Median"].values
                    - df_future["5. adjusted close"].values
                )
                / df_future["5. adjusted close"].values,
                lw=2,
                c="red",
            )
            plt.scatter(
                df_future.index,
                100
                * (
                    df_quantiles["Median"].values
                    - df_future["5. adjusted close"].values
                )
                / df_future["5. adjusted close"].values,
                c="red",
                lw=5,
            )
            plt.plot(
                [df_stock.index[-1], df_future.index[0]],
                [
                    0,
                    100
                    * (
                        df_quantiles["Median"].values[0]
                        - df_future["5. adjusted close"].values[0]
                    )
                    / df_future["5. adjusted close"].values[0],
                ],
                lw=2,
                ls="--",
                c="red",
            )
            plt.fill_between(
                df_pred.index,
                100
                * (
                    df_quantiles["Quantile 10%"].values
                    - df_future["5. adjusted close"].values
                )
                / df_future["5. adjusted close"].values,
                100
                * (
                    df_quantiles["Quantile 90%"].values
                    - df_future["5. adjusted close"].values
                )
                / df_future["5. adjusted close"].values,
                alpha=0.30,
                color="red",
                interpolate=True,
            )
        plt.title("BACKTESTING: Error between Real data and Prediction [%]")

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

        # Refactor prediction dataframe for backtesting print
        if ns_parser.n_loops == 1:
            df_pred.rename(columns={df_pred.columns[0]: "Prediction"}, inplace=True)

        else:
            df_pred = pd.DataFrame()
            df_pred["Prediction"] = df_quantiles["Median"]

        df_pred["Real"] = df_future["5. adjusted close"]

        if gtff.USE_COLOR:
            patch_pandas_text_adjustment()

            print("Time         Real [$]  x  Prediction [$]")
            print(df_pred.apply(price_prediction_backtesting_color, axis=1).to_string())
        else:
            print(df_pred[["Real", "Prediction"]].round(2).to_string())

        print("")
        print_prediction_kpis(df_pred["Real"].values, df_pred["Prediction"].values)
        print("")

    else:
        patch_pandas_text_adjustment()
        # Print prediction data
        print_pretty_prediction_nn(df_pred, df_stock["5. adjusted close"].values[-1])
        print("")

        if ns_parser.n_loops > 1:
            print("Prediction Stats:")
            print(df_quantiles.round(2).to_string())
            print("")


def mlp(other_args: List[str], s_ticker: str, df_stock: pd.DataFrame):
    """
    Train a multi-layer perceptron model
    Parameters
    ----------
    other_args: List[str]
        Argparse Arguments
    s_ticker: str
        Ticker
    df_stock: pd.DataFrame
        Loaded stock dataframe

    Returns
    -------

    """
    try:
        ns_parser = _parse_args(
            prog="mlp", description="""Multilayer Perceptron. """, other_args=other_args
        )
        if not ns_parser:
            return

        # Setup backtesting
        df_stock, df_future = _setup_backtesting(df_stock, ns_parser)

        # Pre-process data
        scaler, stock_train_data, stock_x, stock_y = _preprocess_split(
            df_stock, ns_parser
        )
        stock_x = np.reshape(stock_x, (stock_x.shape[0], stock_x.shape[1]))
        stock_y = np.reshape(stock_y, (stock_y.shape[0], stock_y.shape[1]))

        # Build Neural Network model
        model = build_neural_network_model(
            cfg_nn_models.MultiLayer_Perceptron, ns_parser.n_inputs, ns_parser.n_days
        )
        model.compile(optimizer=ns_parser.s_optimizer, loss=ns_parser.s_loss)

        for idx_loop in range(ns_parser.n_loops):
            # Train our model
            model.fit(
                stock_x,
                stock_y,
                epochs=ns_parser.n_epochs,
                batch_size=ns_parser.n_batch_size,
                verbose=1,
            )
            print("")

            print(model.summary())
            print("")

            # Prediction
            yhat = model.predict(
                stock_train_data[-ns_parser.n_inputs :].reshape(1, ns_parser.n_inputs),
                verbose=0,
            )

            if idx_loop == 0:
                # Re-scale the data back, plot, and print the results
                df_pred = _rescale_data(
                    df_stock, ns_parser, scaler, yhat, idx_loop
                ).to_frame()
            else:
                df_pred = df_pred.join(
                    _rescale_data(
                        df_stock, ns_parser, scaler, yhat, idx_loop
                    ).to_frame()
                )

        _plot_and_print_results(
            df_stock, ns_parser, df_future, df_pred, "MLP", s_ticker
        )

    except Exception as e:
        print(e)
        traceback.print_exc()
        print("")

    finally:
        _restore_env()


def rnn(other_args: List[str], s_ticker: str, df_stock: pd.DataFrame):
    """
    Train a Recurrent Neural Network (rnn)
    Parameters
    ----------
    other_args:List[str]
        Argparse arguments
    s_ticker: str
        Stock ticker
    df_stock: pd.DataFrame
        Dataframe of stock prices

    Returns
    -------

    """
    try:
        ns_parser = _parse_args(
            prog="rnn",
            description="""Recurrent Neural Network. """,
            other_args=other_args,
        )
        if not ns_parser:
            return

        # Setup backtesting
        df_stock, df_future = _setup_backtesting(df_stock, ns_parser)

        # Pre-process data
        scaler, stock_train_data, stock_x, stock_y = _preprocess_split(
            df_stock, ns_parser
        )
        stock_x = np.reshape(stock_x, (stock_x.shape[0], stock_x.shape[1], 1))
        stock_y = np.reshape(stock_y, (stock_y.shape[0], stock_y.shape[1], 1))

        # Build Neural Network model
        model = build_neural_network_model(
            cfg_nn_models.Recurrent_Neural_Network, ns_parser.n_inputs, ns_parser.n_days
        )
        model.compile(optimizer=ns_parser.s_optimizer, loss=ns_parser.s_loss)

        for idx_loop in range(ns_parser.n_loops):
            # Train our model
            model.fit(
                stock_x,
                stock_y,
                epochs=ns_parser.n_epochs,
                batch_size=ns_parser.n_batch_size,
                verbose=1,
            )
            print("")

            print(model.summary())
            print("")

            # Prediction
            yhat = model.predict(
                stock_train_data[-ns_parser.n_inputs :].reshape(
                    1, ns_parser.n_inputs, 1
                ),
                verbose=0,
            )

            if idx_loop == 0:
                # Re-scale the data back, plot, and print the results
                df_pred = _rescale_data(
                    df_stock, ns_parser, scaler, yhat, idx_loop
                ).to_frame()
            else:
                df_pred = df_pred.join(
                    _rescale_data(
                        df_stock, ns_parser, scaler, yhat, idx_loop
                    ).to_frame()
                )

        _plot_and_print_results(
            df_stock, ns_parser, df_future, df_pred, "RNN", s_ticker
        )

    except Exception as e:
        print(e)
        traceback.print_exc()
        print("")

    finally:
        _restore_env()


def lstm(other_args: List[str], s_ticker: str, df_stock: pd.DataFrame):
    """
    Train a Long-Short-Term-Memory Neural Net (lstm)
    Parameters
    ----------
    other_args:List[str]
        Argparse arguments
    s_ticker: str
        Stock ticker
    df_stock: pd.DataFrame
        Dataframe of stock prices

    Returns
    -------

    """
    try:
        ns_parser = _parse_args(
            prog="lstm",
            description="""Long-Short Term Memory. """,
            other_args=other_args,
        )
        if not ns_parser:
            return
        (
            X_train,
            X_valid,
            y_train,
            y_valid,
            X_dates_train,
            X_dates_valid,
            y_dates_train,
            y_dates_valid,
            forecast_data,
            dates_valid,
            scaler,
        ) = prepare_scale_train_valid_test(df_stock["5. adjusted close"], ns_parser)
        # Build Neural Network model
        model = build_neural_network_model(
            cfg_nn_models.Long_Short_Term_Memory, ns_parser.n_inputs, ns_parser.n_days
        )
        model.compile(optimizer=ns_parser.s_optimizer, loss=ns_parser.s_loss)
        print(X_train.shape, X_valid.shape)
        model.fit(
            X_train.reshape(X_train.shape[0], X_train.shape[1], 1),
            y_train,
            epochs=ns_parser.n_epochs,
            verbose=True,
            validation_data=(X_valid, y_valid),
        )

        preds = model.predict(X_valid.reshape(X_valid.shape[0], X_valid.shape[1], 1))

        plt.scatter(df_stock.index, df_stock["5. adjusted close"].values, s= 3)
        for i in range(len(y_valid)):
            plt.plot(y_dates_valid[i], scaler.inverse_transform(preds[i].reshape(-1,1)), "r", lw=3)
            plt.fill_between(y_dates_valid[i], scaler.inverse_transform(preds[i].reshape(-1,1)),
                             scaler.inverse_transform(y_valid[i].reshape(-1,1)))
        plt.show()
        # for idx_loop in range(ns_parser.n_loops):
        # Train our model
        #    model.fit(
        #        stock_x,
        #        stock_y,
        #        epochs=ns_parser.n_epochs,
        #        batch_size=ns_parser.n_batch_size,
        #        verbose=1,
        #    )
        #    print("")

        #    print(model.summary())
        #    print("")

        #    # Prediction
        #    yhat = model.predict(
        #        stock_train_data[-ns_parser.n_inputs :].reshape(
        #            1, ns_parser.n_inputs, 1
        #        ),
        #        verbose=0,
        #    )

        #    if idx_loop == 0:
        # Re-scale the data back, plot, and print the results
        #        df_pred = _rescale_data(
        #            df_stock, ns_parser, scaler, yhat, idx_loop
        #        ).to_frame()
        #    else:
        #        df_pred = df_pred.join(
        #            _rescale_data(
        #                df_stock, ns_parser, scaler, yhat, idx_loop
        #            ).to_frame()
        #        )

        # _plot_and_print_results(
        #    df_stock, ns_parser, df_future, df_pred, "LSTM", s_ticker
        # )

    except Exception as e:
        print(e)
        traceback.print_exc()
        print("")

    finally:
        _restore_env()

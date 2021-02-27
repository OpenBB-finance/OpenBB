import argparse
from gamestonk_terminal.helper_funcs import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()

from TimeSeriesCrossValidation import splitTrain

from sklearn.preprocessing import MinMaxScaler, StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    LSTM,
    SimpleRNN,
    Dense,
    Dropout,
    Activation,
    RepeatVector,
    TimeDistributed,
)

from gamestonk_terminal import config_neural_network_models as cfg_nn_models

import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

from warnings import simplefilter

simplefilter(action="ignore", category=FutureWarning)


# ----------------------------------------------------------------------------------------------------
def build_neural_network_model(Recurrent_Neural_Network, n_inputs, n_days):
    model = Sequential()

    for idx_layer, d_layer in enumerate(Recurrent_Neural_Network):
        # Recurrent Neural Network
        if str(*d_layer) is "SimpleRNN":
            # Is this the input layer? If so, define input_shape
            if idx_layer == 0:
                model.add(SimpleRNN(**d_layer["SimpleRNN"], input_shape=(n_inputs, 1)))
            # Is this the last output layer? If so, set units to prediction days
            elif idx_layer == (len(Recurrent_Neural_Network) - 1):
                model.add(SimpleRNN(**d_layer["SimpleRNN"], units=n_days))
            else:
                model.add(SimpleRNN(**d_layer["SimpleRNN"]))

        # Long-Short Term-Memory
        elif str(*d_layer) is "LSTM":
            # Is this the input layer? If so, define input_shape
            if idx_layer == 0:
                model.add(LSTM(**d_layer["LSTM"], input_shape=(n_inputs, 1)))
            # Is this the last output layer? If so, set units to prediction days
            elif idx_layer == (len(Recurrent_Neural_Network) - 1):
                model.add(LSTM(**d_layer["LSTM"], units=n_days))
            else:
                model.add(LSTM(**d_layer["LSTM"]))

        # Dense (Simple Neuron)
        elif str(*d_layer) is "Dense":
            # Is this the input layer? If so, define input_shape
            if idx_layer == 0:
                model.add(Dense(**d_layer["Dense"], input_dim=n_inputs))
            # Is this the last output layer? If so, set units to prediction days
            elif idx_layer == (len(Recurrent_Neural_Network) - 1):
                model.add(Dense(**d_layer["Dense"], units=n_days))
            else:
                model.add(Dense(**d_layer["Dense"]))

        # Dropout (Regularization)
        elif str(*d_layer) is "Dropout":
            model.add(Dropout(**d_layer["Dropout"]))

        else:
            print(f"Incorrect neuron type: {str(*d_layer)}")

    return model


# -------------------------------------------------- MLP --------------------------------------------------
def mlp(l_args, s_ticker, s_interval, df_stock):
    parser = argparse.ArgumentParser(
        prog="mlp", description="""Multilayer Perceptron. """
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
        "-e",
        "--epochs",
        action="store",
        dest="n_epochs",
        type=check_positive,
        default=200,
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
        default="normalization",
        choices=["normalization", "standardization", "none"],
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
            "optimizer",
            "rmsprop",
            "sgd",
        ],
        help="optimization technique.",
    )
    parser.add_argument(
        "-l",
        "--loss",
        action="store",
        dest="s_loss",
        default="mae",
        choices=["mae", "mape", "mse", "msle"],
        help="loss function.",
    )

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        # Pre-process data
        if ns_parser.s_preprocessing == "standardization":
            scaler = StandardScaler()
            stock_train_data = scaler.fit_transform(
                np.array(df_stock["5. adjusted close"].values.reshape(-1, 1))
            )
        elif ns_parser.s_preprocessing == "normalization":
            scaler = MinMaxScaler()
            stock_train_data = scaler.fit_transform(
                np.array(df_stock["5. adjusted close"].values.reshape(-1, 1))
            )
        else:  # No pre-processing
            stock_train_data = np.array(
                df_stock["5. adjusted close"].values.reshape(-1, 1)
            )

        # Split training data for the neural network
        stock_x, stock_y = splitTrain.split_train(
            stock_train_data,
            ns_parser.n_inputs,
            ns_parser.n_days,
            numJumps=ns_parser.n_jumps,
        )
        stock_x = np.array(stock_x)
        stock_x = np.reshape(stock_x, (stock_x.shape[0], stock_x.shape[1]))
        stock_y = np.array(stock_y)
        stock_y = np.reshape(stock_y, (stock_y.shape[0], stock_y.shape[1]))

        # Build Neural Network model
        model = build_neural_network_model(
            cfg_nn_models.MultiLayer_Perceptron, ns_parser.n_inputs, ns_parser.n_days
        )
        model.compile(optimizer=ns_parser.s_optimizer, loss=ns_parser.s_loss)

        # Train our model
        model.fit(stock_x, stock_y, epochs=ns_parser.n_epochs, verbose=1)
        print("")

        print(model.summary())
        print("")

        # Prediction
        yhat = model.predict(
            stock_train_data[-ns_parser.n_inputs :].reshape(1, ns_parser.n_inputs),
            verbose=0,
        )

        # Re-scale the data back
        if (ns_parser.s_preprocessing == "standardization") or (
            ns_parser.s_preprocessing == "normalization"
        ):
            y_pred_test_t = scaler.inverse_transform(yhat.tolist())
        else:
            y_pred_test_t = yhat

        l_pred_days = get_next_stock_market_days(
            last_stock_day=df_stock["5. adjusted close"].index[-1],
            n_next_days=ns_parser.n_days,
        )
        df_pred = pd.Series(y_pred_test_t[0].tolist(), index=l_pred_days, name="Price")

        # Plotting
        plt.plot(df_stock.index, df_stock["5. adjusted close"], lw=3)
        plt.title(f"MLP on {s_ticker} - {ns_parser.n_days} days prediction")
        plt.xlim(
            df_stock.index[0], get_next_stock_market_days(df_pred.index[-1], 1)[-1]
        )
        plt.xlabel("Time")
        plt.ylabel("Share Price ($)")
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
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
        xmin, xmax, ymin, ymax = plt.axis()
        plt.vlines(
            df_stock.index[-1],
            ymin,
            ymax,
            colors="k",
            linewidth=3,
            linestyle="--",
            color="k",
        )
        plt.show()

        # Print prediction data
        print("Predicted share price:")
        df_pred = df_pred.apply(lambda x: f"{x:.2f} $")
        print(df_pred.to_string())
        print("")

    except:
        print("")


# -------------------------------------------------- RNN --------------------------------------------------
def rnn(l_args, s_ticker, s_interval, df_stock):
    parser = argparse.ArgumentParser(
        prog="rnn", description="""Recurrent Neural Network. """
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
        "-e",
        "--epochs",
        action="store",
        dest="n_epochs",
        type=check_positive,
        default=200,
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
        default="normalization",
        choices=["normalization", "standardization", "none"],
        help="pre-processing data.",
    )
    parser.add_argument(
        "-o",
        "--optimizer",
        action="store",
        dest="s_optimizer",
        default="adam",
        help="optimizer technique",
        choices=[
            "adam",
            "adagrad",
            "adadelta",
            "adamax",
            "ftrl",
            "nadam",
            "optimizer",
            "rmsprop",
            "sgd",
        ],
    )
    parser.add_argument(
        "-l",
        "--loss",
        action="store",
        dest="s_loss",
        default="mae",
        choices=["mae", "mape", "mse", "msle"],
        help="loss function.",
    )

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        # Pre-process data
        if ns_parser.s_preprocessing == "standardization":
            scaler = StandardScaler()
            stock_train_data = scaler.fit_transform(
                np.array(df_stock["5. adjusted close"].values.reshape(-1, 1))
            )
        elif ns_parser.s_preprocessing == "normalization":
            scaler = MinMaxScaler()
            stock_train_data = scaler.fit_transform(
                np.array(df_stock["5. adjusted close"].values.reshape(-1, 1))
            )
        else:  # No pre-processing
            stock_train_data = np.array(
                df_stock["5. adjusted close"].values.reshape(-1, 1)
            )

        # Split training data for the neural network
        stock_x, stock_y = splitTrain.split_train(
            stock_train_data,
            ns_parser.n_inputs,
            ns_parser.n_days,
            numJumps=ns_parser.n_jumps,
        )
        stock_x = np.array(stock_x)
        stock_x = np.reshape(stock_x, (stock_x.shape[0], stock_x.shape[1], 1))
        stock_y = np.array(stock_y)
        stock_y = np.reshape(stock_y, (stock_y.shape[0], stock_y.shape[1], 1))

        # Build Neural Network model
        model = build_neural_network_model(
            cfg_nn_models.Recurrent_Neural_Network, ns_parser.n_inputs, ns_parser.n_days
        )
        model.compile(optimizer=ns_parser.s_optimizer, loss=ns_parser.s_loss)

        # Train our model
        model.fit(stock_x, stock_y, epochs=ns_parser.n_epochs, verbose=1)
        print("")

        print(model.summary())
        print("")

        # Prediction
        yhat = model.predict(
            stock_train_data[-ns_parser.n_inputs :].reshape(1, ns_parser.n_inputs, 1),
            verbose=0,
        )

        # Re-scale the data back
        if (ns_parser.s_preprocessing == "standardization") or (
            ns_parser.s_preprocessing == "normalization"
        ):
            y_pred_test_t = scaler.inverse_transform(yhat.tolist())
        else:
            y_pred_test_t = yhat

        l_pred_days = get_next_stock_market_days(
            last_stock_day=df_stock["5. adjusted close"].index[-1],
            n_next_days=ns_parser.n_days,
        )
        df_pred = pd.Series(y_pred_test_t[0].tolist(), index=l_pred_days, name="Price")

        # Plotting
        plt.plot(df_stock.index, df_stock["5. adjusted close"], lw=3)
        plt.title(f"RNN on {s_ticker} - {ns_parser.n_days} days prediction")
        plt.xlim(
            df_stock.index[0], get_next_stock_market_days(df_pred.index[-1], 1)[-1]
        )
        plt.xlabel("Time")
        plt.ylabel("Share Price ($)")
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
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
        xmin, xmax, ymin, ymax = plt.axis()
        plt.vlines(
            df_stock.index[-1],
            ymin,
            ymax,
            colors="k",
            linewidth=3,
            linestyle="--",
            color="k",
        )
        plt.show()

        # Print prediction data
        print("Predicted share price:")
        df_pred = df_pred.apply(lambda x: f"{x:.2f} $")
        print(df_pred.to_string())
        print("")

    except:
        print("")


# -------------------------------------------------- LSTM --------------------------------------------------
def lstm(l_args, s_ticker, s_interval, df_stock):
    parser = argparse.ArgumentParser(
        prog="lstm", description="""Long-Short Term Memory. """
    )

    parser.add_argument(
        "-d",
        "--days",
        action="store",
        dest="n_days",
        type=check_positive,
        default=5,
        help="prediction days",
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
        "-e",
        "--epochs",
        action="store",
        dest="n_epochs",
        type=check_positive,
        default=200,
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
        default="normalization",
        choices=["normalization", "standardization", "none"],
        help="pre-processing data.",
    )
    parser.add_argument(
        "-o",
        "--optimizer",
        action="store",
        dest="s_optimizer",
        default="adam",
        help="optimization technique.",
        choices=[
            "adam",
            "adagrad",
            "adadelta",
            "adamax",
            "ftrl",
            "nadam",
            "optimizer",
            "rmsprop",
            "sgd",
        ],
    )
    parser.add_argument(
        "-l",
        "--loss",
        action="store",
        dest="s_loss",
        default="mae",
        choices=["mae", "mape", "mse", "msle"],
        help="loss function.",
    )

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        # Pre-process data
        if ns_parser.s_preprocessing == "standardization":
            scaler = StandardScaler()
            stock_train_data = scaler.fit_transform(
                np.array(df_stock["5. adjusted close"].values.reshape(-1, 1))
            )
        elif ns_parser.s_preprocessing == "normalization":
            scaler = MinMaxScaler()
            stock_train_data = scaler.fit_transform(
                np.array(df_stock["5. adjusted close"].values.reshape(-1, 1))
            )
        else:  # No pre-processing
            stock_train_data = np.array(
                df_stock["5. adjusted close"].values.reshape(-1, 1)
            )

        # Split training data for the neural network
        stock_x, stock_y = splitTrain.split_train(
            stock_train_data,
            ns_parser.n_inputs,
            ns_parser.n_days,
            numJumps=ns_parser.n_jumps,
        )
        stock_x = np.array(stock_x)
        stock_x = np.reshape(stock_x, (stock_x.shape[0], stock_x.shape[1], 1))
        stock_y = np.array(stock_y)
        stock_y = np.reshape(stock_y, (stock_y.shape[0], stock_y.shape[1], 1))

        # Build Neural Network model
        model = build_neural_network_model(
            cfg_nn_models.Long_Short_Term_Memory, ns_parser.n_inputs, ns_parser.n_days
        )
        model.compile(optimizer=ns_parser.s_optimizer, loss=ns_parser.s_loss)

        # Train our model
        model.fit(stock_x, stock_y, epochs=ns_parser.n_epochs, verbose=1)
        print("")

        print(model.summary())
        print("")

        # Prediction
        yhat = model.predict(
            stock_train_data[-ns_parser.n_inputs :].reshape(1, ns_parser.n_inputs, 1),
            verbose=0,
        )

        # Re-scale the data back
        if (ns_parser.s_preprocessing == "standardization") or (
            ns_parser.s_preprocessing == "normalization"
        ):
            y_pred_test_t = scaler.inverse_transform(yhat.tolist())
        else:
            y_pred_test_t = yhat

        l_pred_days = get_next_stock_market_days(
            last_stock_day=df_stock["5. adjusted close"].index[-1],
            n_next_days=ns_parser.n_days,
        )
        df_pred = pd.Series(y_pred_test_t[0].tolist(), index=l_pred_days, name="Price")

        # Plotting
        plt.plot(df_stock.index, df_stock["5. adjusted close"], lw=3)
        plt.title(f"LSTM on {s_ticker} - {ns_parser.n_days} days prediction")
        plt.xlim(
            df_stock.index[0], get_next_stock_market_days(df_pred.index[-1], 1)[-1]
        )
        plt.xlabel("Time")
        plt.ylabel("Share Price ($)")
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
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
        xmin, xmax, ymin, ymax = plt.axis()
        plt.vlines(
            df_stock.index[-1],
            ymin,
            ymax,
            colors="k",
            linewidth=3,
            linestyle="--",
            color="k",
        )
        plt.show()

        # Print prediction data
        print("Predicted share price:")
        df_pred = df_pred.apply(lambda x: f"{x:.2f} $")
        print(df_pred.to_string())
        print("")

    except:
        print("")

import argparse
import datetime
import os
from warnings import simplefilter
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from TimeSeriesCrossValidation import splitTrain
from sklearn.preprocessing import MinMaxScaler, StandardScaler
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
    print_pretty_prediction,
    price_prediction_backtesting_color,
    print_prediction_kpis,
)

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff

from gamestonk_terminal import config_neural_network_models as cfg_nn_models


register_matplotlib_converters()

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

simplefilter(action="ignore", category=FutureWarning)


def build_neural_network_model(Recurrent_Neural_Network, n_inputs, n_days):
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


def mlp(l_args, s_ticker, df_stock):
    parser = argparse.ArgumentParser(
        add_help=False, prog="mlp", description="""Multilayer Perceptron. """
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
    parser.add_argument(
        "-e",
        "--end",
        action="store",
        type=valid_date,
        dest="s_end_date",
        default=None,
        help="The end date (format YYYY-MM-DD) to select - Backtesting",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)
        if not ns_parser:
            return

        # BACKTESTING
        if ns_parser.s_end_date:

            if ns_parser.s_end_date < df_stock.index[0]:
                print(
                    "Backtesting not allowed, since End Date is older than Start Date of historical data\n"
                )
                return

            if ns_parser.s_end_date < get_next_stock_market_days(
                last_stock_day=df_stock.index[0],
                n_next_days=ns_parser.n_inputs + ns_parser.n_days,
            )[-1]:
                print(
                    "Backtesting not allowed, since End Date is too close to Start Date to train model\n"
                )
                return

            future_index = get_next_stock_market_days(
                last_stock_day=ns_parser.s_end_date, n_next_days=ns_parser.n_days
            )

            if future_index[-1] > datetime.datetime.now():
                print(
                    "Backtesting not allowed, since End Date + Prediction days is in the future\n"
                )
                return

            df_future = df_stock[future_index[0] : future_index[-1]]
            df_stock = df_stock[: ns_parser.s_end_date]

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

        if not stock_x:
            print("Given the model parameters more training data is needed.\n")
            return

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
        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
        plt.plot(df_stock.index, df_stock["5. adjusted close"], lw=3)
        # BACKTESTING
        if ns_parser.s_end_date:
            plt.title(
                f"BACKTESTING: MLP on {s_ticker} - {ns_parser.n_days} days prediction"
            )
        else:
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
            plt.plot(df_pred.index, df_pred, lw=2, c="green")
            plt.scatter(
                df_future.index, df_future["5. adjusted close"], c="tab:blue", lw=3
            )
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

            # Refactor prediction dataframe for backtesting print
            df_pred.name = "Prediction"
            df_pred = df_pred.to_frame()
            df_pred["Real"] = df_future["5. adjusted close"]

            if gtff.USE_COLOR:

                patch_pandas_text_adjustment()

                print("Time         Real [$]  x  Prediction [$]")
                print(
                    df_pred.apply(
                        price_prediction_backtesting_color, axis=1
                    ).to_string()
                )
            else:
                print(df_pred[["Real", "Prediction"]].round(2).to_string())

            print("")
            print_prediction_kpis(df_pred["Real"].values, df_pred["Prediction"].values)

        else:
            # Print prediction data
            print_pretty_prediction(df_pred, df_stock["5. adjusted close"].values[-1])
        print("")

    except Exception as e:
        print(e)
        print("")


def rnn(l_args, s_ticker, df_stock):
    parser = argparse.ArgumentParser(
        add_help=False, prog="rnn", description="""Recurrent Neural Network. """
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
    parser.add_argument(
        "-e",
        "--end",
        action="store",
        type=valid_date,
        dest="s_end_date",
        default=None,
        help="The end date (format YYYY-MM-DD) to select - Backtesting",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)
        if not ns_parser:
            return

        # BACKTESTING
        if ns_parser.s_end_date:

            if ns_parser.s_end_date < df_stock.index[0]:
                print(
                    "Backtesting not allowed, since End Date is older than Start Date of historical data\n"
                )
                return

            if ns_parser.s_end_date < get_next_stock_market_days(
                last_stock_day=df_stock.index[0],
                n_next_days=ns_parser.n_inputs + ns_parser.n_days,
            )[-1]:
                print(
                    "Backtesting not allowed, since End Date is too close to Start Date to train model\n"
                )
                return

            future_index = get_next_stock_market_days(
                last_stock_day=ns_parser.s_end_date, n_next_days=ns_parser.n_days
            )

            if future_index[-1] > datetime.datetime.now():
                print(
                    "Backtesting not allowed, since End Date + Prediction days is in the future\n"
                )
                return

            df_future = df_stock[future_index[0] : future_index[-1]]
            df_stock = df_stock[: ns_parser.s_end_date]

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

        if not stock_x:
            print("Given the model parameters more training data is needed.\n")
            return

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
        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
        plt.plot(df_stock.index, df_stock["5. adjusted close"], lw=3)
        # BACKTESTING
        if ns_parser.s_end_date:
            plt.title(
                f"BACKTESTING: RNN on {s_ticker} - {ns_parser.n_days} days prediction"
            )
        else:
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
            plt.plot(df_pred.index, df_pred, lw=2, c="green")
            plt.scatter(
                df_future.index, df_future["5. adjusted close"], c="tab:blue", lw=3
            )
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

            # Refactor prediction dataframe for backtesting print
            df_pred.name = "Prediction"
            df_pred = df_pred.to_frame()
            df_pred["Real"] = df_future["5. adjusted close"]

            if gtff.USE_COLOR:

                patch_pandas_text_adjustment()

                print("Time         Real [$]  x  Prediction [$]")
                print(
                    df_pred.apply(
                        price_prediction_backtesting_color, axis=1
                    ).to_string()
                )
            else:
                print(df_pred[["Real", "Prediction"]].round(2).to_string())

            print("")
            print_prediction_kpis(df_pred["Real"].values, df_pred["Prediction"].values)

        else:
            # Print prediction data
            print_pretty_prediction(df_pred, df_stock["5. adjusted close"].values[-1])
        print("")

    except Exception as e:
        print(e)
        print("")


def lstm(l_args, s_ticker, df_stock):
    parser = argparse.ArgumentParser(
        add_help=False, prog="lstm", description="""Long-Short Term Memory. """
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
    parser.add_argument(
        "-e",
        "--end",
        action="store",
        type=valid_date,
        dest="s_end_date",
        default=None,
        help="The end date (format YYYY-MM-DD) to select - Backtesting",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)
        if not ns_parser:
            return

        # BACKTESTING
        if ns_parser.s_end_date:

            if ns_parser.s_end_date < df_stock.index[0]:
                print(
                    "Backtesting not allowed, since End Date is older than Start Date of historical data\n"
                )
                return

            if ns_parser.s_end_date < get_next_stock_market_days(
                last_stock_day=df_stock.index[0],
                n_next_days=ns_parser.n_inputs + ns_parser.n_days,
            )[-1]:
                print(
                    "Backtesting not allowed, since End Date is too close to Start Date to train model\n"
                )
                return

            future_index = get_next_stock_market_days(
                last_stock_day=ns_parser.s_end_date, n_next_days=ns_parser.n_days
            )

            if future_index[-1] > datetime.datetime.now():
                print(
                    "Backtesting not allowed, since End Date + Prediction days is in the future\n"
                )
                return

            df_future = df_stock[future_index[0] : future_index[-1]]
            df_stock = df_stock[: ns_parser.s_end_date]

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

        if not stock_x:
            print("Given the model parameters more training data is needed.\n")
            return

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
        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
        plt.plot(df_stock.index, df_stock["5. adjusted close"], lw=3)
        # BACKTESTING
        if ns_parser.s_end_date:
            plt.title(
                f"BACKTESTING: LSTM on {s_ticker} - {ns_parser.n_days} days prediction"
            )
        else:
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
            plt.plot(df_pred.index, df_pred, lw=2, c="green")
            plt.scatter(
                df_future.index, df_future["5. adjusted close"], c="tab:blue", lw=3
            )
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

            # Refactor prediction dataframe for backtesting print
            df_pred.name = "Prediction"
            df_pred = df_pred.to_frame()
            df_pred["Real"] = df_future["5. adjusted close"]

            if gtff.USE_COLOR:

                patch_pandas_text_adjustment()

                print("Time         Real [$]  x  Prediction [$]")
                print(
                    df_pred.apply(
                        price_prediction_backtesting_color, axis=1
                    ).to_string()
                )
            else:
                print(df_pred[["Real", "Prediction"]].round(2).to_string())

            print("")
            print_prediction_kpis(df_pred["Real"].values, df_pred["Prediction"].values)

        else:
            # Print prediction data
            print_pretty_prediction(df_pred, df_stock["5. adjusted close"].values[-1])
        print("")

    except Exception as e:
        print(e)
        print("")

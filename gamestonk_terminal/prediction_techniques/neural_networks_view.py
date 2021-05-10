""" Neural Networks View"""
__docformat__ = "numpy"

from typing import List, Any
import traceback
import numpy as np
import pandas as pd
from keras.callbacks import EarlyStopping
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    LSTM,
    SimpleRNN,
    Dense,
    Dropout,
    Conv1D,
    MaxPool1D,
    AvgPool1D,
    Flatten,
)
from gamestonk_terminal.helper_funcs import get_next_stock_market_days
from gamestonk_terminal.prediction_techniques.pred_helper import (
    prepare_scale_train_valid_test,
    forecast,
    plot_data_predictions,
    parse_args,
    restore_env,
)
from gamestonk_terminal import config_neural_network_models as cfg_nn_models

es = EarlyStopping(monitor="val_loss", patience=10)

def build_neural_network_model(
    Recurrent_Neural_Network: List[Any], n_inputs: int, n_days: int
):
    """
    Builds neural netfrom config_neural_network_models.py
    Parameters
    ----------
    Recurrent_Neural_Network: List[Any]
        List of layers with parameters as a dictionary in the file
    n_inputs: int
        Number of days that will be fed into the NN
    n_days: int
        Number of days the NN wants to predict

    Returns
    -------
    model:
        Keras sequential model with layers from the file

    """
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

        # Conv1D Layer
        elif str(*d_layer) == "Conv1D":
            if idx_layer == 0:
                model.add(Conv1D(**d_layer["Conv1D"], input_shape=(n_inputs, 1)))
            else:
                model.add(Conv1D(**d_layer["Conv1D"]))
        # Max Pooling Layer for after Conv Layer
        elif str(*d_layer) == "MaxPool1D":
            model.add(MaxPool1D(**d_layer["MaxPool1D"]))
        # Allow for if user wants to do average pooling
        elif str(*d_layer) == "AvgPool1D":
            model.add(AvgPool1D(**d_layer["AvgPool1D"]))
        # Dropout (Regularization)
        elif str(*d_layer) == "Dropout":
            model.add(Dropout(**d_layer["Dropout"]))
        # Flatten layer for Convolutions
        elif str(*d_layer) == "Flatten":
            model.add(Flatten())
        else:
            print(f"Incorrect neuron type: {str(*d_layer)}")

    return model


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

    """
    try:
        ns_parser = parse_args(
            prog="mlp",
            description="""Multi-Layered-Perceptron. """,
            other_args=other_args,
        )
        if not ns_parser:
            return
        (
            X_train,
            X_valid,
            y_train,
            y_valid,
            _,
            _,
            _,
            y_dates_valid,
            forecast_data_input,
            dates_forecast_input,
            scaler,
            is_error,
        ) = prepare_scale_train_valid_test(df_stock["5. adjusted close"], ns_parser)
        if is_error:
            return
        print(
            f"Training on {X_train.shape[0]} samples.  Using {X_valid.shape[0]} samples for validation."
            f" {ns_parser.n_loops} loops"
        )
        future_dates = get_next_stock_market_days(
            dates_forecast_input[-1], n_next_days=ns_parser.n_days
        )

        preds = np.zeros((ns_parser.n_loops, X_valid.shape[0], ns_parser.n_days))
        forecast_data = np.zeros((ns_parser.n_loops, ns_parser.n_days))
        for i in range(ns_parser.n_loops):
            # Build Neural Network model
            model = build_neural_network_model(
                cfg_nn_models.Long_Short_Term_Memory,
                ns_parser.n_inputs,
                ns_parser.n_days,
            )
            model.compile(optimizer=ns_parser.s_optimizer, loss=ns_parser.s_loss)

            model.fit(
                X_train.reshape(X_train.shape[0], X_train.shape[1], 1),
                y_train,
                epochs=ns_parser.n_epochs,
                verbose=True,
                batch_size=ns_parser.n_batch_size,
                validation_data=(X_valid, y_valid),
                callbacks=[es],
            )

            preds[i] = model.predict(
                X_valid.reshape(X_valid.shape[0], X_valid.shape[1], 1)
            ).reshape(X_valid.shape[0], ns_parser.n_days)
            forecast_data[i] = forecast(
                forecast_data_input, future_dates, model, scaler
            ).values.flat

        forecast_data_df = pd.DataFrame(forecast_data.T, index=future_dates)
        print(forecast_data_df)
        plot_data_predictions(
            df_stock,
            np.median(preds, axis=0),
            y_valid,
            y_dates_valid,
            scaler,
            f"MLP Model on {s_ticker}",
            forecast_data_df,
            ns_parser.n_loops,
        )
        print("")

    except Exception as e:
        print(e)
        traceback.print_exc()
        print("")

    finally:
        restore_env()


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

    """
    try:
        ns_parser = parse_args(
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
            _,
            _,
            _,
            y_dates_valid,
            forecast_data_input,
            dates_forecast_input,
            scaler,
            is_error,
        ) = prepare_scale_train_valid_test(df_stock["5. adjusted close"], ns_parser)
        if is_error:
            return
        print(
            f"Training on {X_train.shape[0]} samples.  Using {X_valid.shape[0]} samples for validation."
            f" {ns_parser.n_loops} loops"
        )
        future_dates = get_next_stock_market_days(
            dates_forecast_input[-1], n_next_days=ns_parser.n_days
        )

        preds = np.zeros((ns_parser.n_loops, X_valid.shape[0], ns_parser.n_days))
        forecast_data = np.zeros((ns_parser.n_loops, ns_parser.n_days))
        for i in range(ns_parser.n_loops):
            # Build Neural Network model
            model = build_neural_network_model(
                cfg_nn_models.Long_Short_Term_Memory,
                ns_parser.n_inputs,
                ns_parser.n_days,
            )
            model.compile(optimizer=ns_parser.s_optimizer, loss=ns_parser.s_loss)

            model.fit(
                X_train.reshape(X_train.shape[0], X_train.shape[1], 1),
                y_train,
                epochs=ns_parser.n_epochs,
                verbose=True,
                batch_size=ns_parser.n_batch_size,
                validation_data=(X_valid, y_valid),
                callbacks=[es],
            )

            preds[i] = model.predict(
                X_valid.reshape(X_valid.shape[0], X_valid.shape[1], 1)
            ).reshape(X_valid.shape[0], ns_parser.n_days)
            forecast_data[i] = forecast(
                forecast_data_input, future_dates, model, scaler
            ).values.flat

        forecast_data_df = pd.DataFrame(forecast_data.T, index=future_dates)
        print(forecast_data_df)
        plot_data_predictions(
            df_stock,
            np.median(preds, axis=0),
            y_valid,
            y_dates_valid,
            scaler,
            f"RNN Model on {s_ticker}",
            forecast_data_df,
            ns_parser.n_loops,
        )
        print("")
    except Exception as e:
        print(e)
        traceback.print_exc()
        print("")

    finally:
        restore_env()


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
    """
    try:
        ns_parser = parse_args(
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
            _,
            _,
            _,
            y_dates_valid,
            forecast_data_input,
            dates_forecast_input,
            scaler,
            is_error,
        ) = prepare_scale_train_valid_test(df_stock["5. adjusted close"], ns_parser)
        if is_error:
            return
        print(
            f"Training on {X_train.shape[0]} samples.  Using {X_valid.shape[0]} samples for validation."
            f" {ns_parser.n_loops} loops"
        )
        future_dates = get_next_stock_market_days(
            dates_forecast_input[-1], n_next_days=ns_parser.n_days
        )

        preds = np.zeros((ns_parser.n_loops, X_valid.shape[0], ns_parser.n_days))
        forecast_data = np.zeros((ns_parser.n_loops, ns_parser.n_days))
        for i in range(ns_parser.n_loops):
            # Build Neural Network model
            model = build_neural_network_model(
                cfg_nn_models.Long_Short_Term_Memory,
                ns_parser.n_inputs,
                ns_parser.n_days,
            )
            model.compile(optimizer=ns_parser.s_optimizer, loss=ns_parser.s_loss)

            model.fit(
                X_train.reshape(X_train.shape[0], X_train.shape[1], 1),
                y_train,
                epochs=ns_parser.n_epochs,
                verbose=True,
                batch_size=ns_parser.n_batch_size,
                validation_data=(X_valid, y_valid),
                callbacks=[es],
            )

            preds[i] = model.predict(
                X_valid.reshape(X_valid.shape[0], X_valid.shape[1], 1)
            ).reshape(X_valid.shape[0], ns_parser.n_days)

            forecast_data[i] = forecast(
                forecast_data_input, future_dates, model, scaler
            ).values.flat

        forecast_data_df = pd.DataFrame(forecast_data.T, index=future_dates)
        print(forecast_data_df)
        plot_data_predictions(
            df_stock,
            np.median(preds, axis=0),
            y_valid,
            y_dates_valid,
            scaler,
            f"LSTM Model on {s_ticker}",
            forecast_data_df,
            ns_parser.n_loops,
        )
        print("")

    except Exception as e:
        print(e)
        traceback.print_exc()
        print("")

    finally:
        restore_env()


def conv1d(other_args: List[str], s_ticker: str, df_stock: pd.DataFrame):
    """
    Train a 1D Convolutional Neural Net (1D CNN)
    Parameters
    ----------
    other_args:List[str]
        Argparse arguments
    s_ticker: str
        Stock ticker
    df_stock: pd.DataFrame
        Dataframe of stock prices
    """
    try:
        ns_parser = parse_args(
            prog="conv1d",
            description="""1D CNN.""",
            other_args=other_args,
        )
        if not ns_parser:
            return
        (
            X_train,
            X_valid,
            y_train,
            y_valid,
            _,
            _,
            _,
            y_dates_valid,
            forecast_data_input,
            dates_forecast_input,
            scaler,
            is_error,
        ) = prepare_scale_train_valid_test(df_stock["5. adjusted close"], ns_parser)
        if is_error:
            return
        print(
            f"Training on {X_train.shape[0]} samples.  Using {X_valid.shape[0]} samples for validation."
            f" {ns_parser.n_loops} loops"
        )
        future_dates = get_next_stock_market_days(
            dates_forecast_input[-1], n_next_days=ns_parser.n_days
        )

        preds = np.zeros((ns_parser.n_loops, X_valid.shape[0], ns_parser.n_days))
        forecast_data = np.zeros((ns_parser.n_loops, ns_parser.n_days))
        for i in range(ns_parser.n_loops):
            # Build Neural Network model
            model = build_neural_network_model(
                cfg_nn_models.Convolutional,
                ns_parser.n_inputs,
                ns_parser.n_days,
            )
            model.compile(optimizer=ns_parser.s_optimizer, loss=ns_parser.s_loss)

            model.fit(
                X_train.reshape(X_train.shape[0], X_train.shape[1], 1),
                y_train,
                epochs=ns_parser.n_epochs,
                verbose=True,
                batch_size=ns_parser.n_batch_size,
                validation_data=(X_valid, y_valid),
                callbacks = [es]
            )

            preds[i] = model.predict(
                X_valid.reshape(X_valid.shape[0], X_valid.shape[1], 1)
            ).reshape(X_valid.shape[0], ns_parser.n_days)
            forecast_data[i] = forecast(
                forecast_data_input, future_dates, model, scaler
            ).values.flat

        forecast_data_df = pd.DataFrame(forecast_data.T, index=future_dates)
        print(forecast_data_df)
        plot_data_predictions(
            df_stock,
            np.median(preds, axis=0),
            y_valid,
            y_dates_valid,
            scaler,
            f"Conv1D Model on {s_ticker}",
            forecast_data_df,
            ns_parser.n_loops,
        )
        print("")

    except Exception as e:
        print(e)
        traceback.print_exc()
        print("")

    finally:
        restore_env()

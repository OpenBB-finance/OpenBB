"""Neural Network Prediction Models"""
__docformat__ = "numpy"

from typing import List, Any, Union, Tuple
import pandas as pd
import numpy as np
from tensorflow.keras.callbacks import EarlyStopping
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
from tensorflow.keras.optimizers import (
    Adam,
    Adamax,
    Adagrad,
    Adadelta,
    Ftrl,
    Nadam,
    RMSprop,
    SGD,
)
from gamestonk_terminal.helper_funcs import get_next_stock_market_days
from gamestonk_terminal.common.prediction_techniques.pred_helper import (
    prepare_scale_train_valid_test,
    forecast,
)
from gamestonk_terminal import config_neural_network_models as cfg_nn_models


optimizers = {
    "Adam": Adam,
    "Adagrad": Adagrad,
    "Adadelta": Adadelta,
    "Adamax": Adamax,
    "Ftrl": Ftrl,
    "Nadam": Nadam,
    "Rmsprop": RMSprop,
    "Sgd": SGD,
}


if cfg_nn_models.Early_Stop_Patience:
    es = EarlyStopping(monitor="val_loss", patience=cfg_nn_models.Early_Stop_Patience)
else:
    # Set patience to very long value
    es = EarlyStopping(monitor="val_loss", patience=1000)

# pylint:disable=too-many-arguments


def build_neural_network_model(
    Layers: List[Any], n_inputs: int, n_days: int
) -> Sequential:
    """
    Builds neural net from config_neural_network_models.py
    Parameters
    ----------
    Layers: List[Any]
        List of layers with parameters as a dictionary in the file
    n_inputs: int
        Number of days that will be fed into the NN
    n_days: int
        Number of days the NN wants to predict

    Returns
    -------
    model: Sequential
        Keras sequential model with layers from the file

    """
    model = Sequential()

    for idx_layer, d_layer in enumerate(Layers):
        # Recurrent Neural Network
        if str(*d_layer) == "SimpleRNN":
            # Is this the input layer? If so, define input_shape
            if idx_layer == 0:
                model.add(SimpleRNN(**d_layer["SimpleRNN"], input_shape=(n_inputs, 1)))
            # Is this the last output layer? If so, set units to prediction days
            elif idx_layer == (len(Layers) - 1):
                model.add(SimpleRNN(**d_layer["SimpleRNN"], units=n_days))
            else:
                model.add(SimpleRNN(**d_layer["SimpleRNN"]))

        # Long-Short Term-Memory
        elif str(*d_layer) == "LSTM":
            # Is this the input layer? If so, define input_shape
            if idx_layer == 0:
                model.add(LSTM(**d_layer["LSTM"], input_shape=(n_inputs, 1)))
            # Is this the last output layer? If so, set units to prediction days
            elif idx_layer == (len(Layers) - 1):
                model.add(LSTM(**d_layer["LSTM"], units=n_days))
            else:
                model.add(LSTM(**d_layer["LSTM"]))

        # Dense (Simple Neuron)
        elif str(*d_layer) == "Dense":
            # Is this the input layer? If so, define input_shape
            if idx_layer == 0:
                model.add(Dense(**d_layer["Dense"], input_dim=n_inputs))
            # Is this the last output layer? If so, set units to prediction days
            elif idx_layer == (len(Layers) - 1):
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


def mlp_model(
    data: Union[pd.Series, pd.DataFrame],
    n_input: int,
    n_predict: int,
    learning_rate: float,
    epochs: int,
    batch_size: int,
    test_size: float,
    n_loops: int,
    no_shuffle: bool,
) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, Any]:
    """Train MLP model on data based on config params

    Parameters
    ----------
    data : Union[pd.Series, pd.DataFrame]
        Data to fit
    n_input : int
        Length of input sequence
    n_predict : int
        Length of output to predict
    learning_rate : float
        Learning rate for optimizer
    epochs : int
        Number of training epochs
    batch_size : int
        Model batch size
    test_size : float
        Fraction of test size
    n_loops : int
        Number of loops to train model
    no_shuffle : bool
        Flag to not shuffle data

    Returns
    -------
    pd.DataFrame
        Dataframe of predictions
    np.array
        Array of validation predictions
    np.array
        Array of validation data
    np.array
        Array of validation x label data
    Any
        Scaler used for data
    """
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
    ) = prepare_scale_train_valid_test(
        data, n_input, n_predict, test_size, "", no_shuffle
    )
    if is_error:
        return pd.DataFrame(), np.array(0), np.array(0), np.array(0), None

    print(
        f"Training on {X_train.shape[0]} sequences of length {X_train.shape[1]}.  Using {X_valid.shape[0]} sequences "
        f" of length {X_valid.shape[1]} for validation. Model will run {n_loops} loops"
    )

    future_dates = get_next_stock_market_days(
        dates_forecast_input[-1], n_next_days=n_predict
    )

    preds = np.zeros((n_loops, X_valid.shape[0], n_predict))
    forecast_data = np.zeros((n_loops, n_predict))
    for i in range(n_loops):
        # Build Neural Network model
        model = build_neural_network_model(
            cfg_nn_models.MultiLayer_Perceptron,
            n_input,
            n_predict,
        )
        model.compile(
            optimizer=optimizers[cfg_nn_models.Optimizer](learning_rate=learning_rate),
            loss=cfg_nn_models.Loss,
        )
        model.fit(
            X_train.reshape(X_train.shape[0], X_train.shape[1]),
            y_train,
            epochs=epochs,
            verbose=True,
            batch_size=batch_size,
            validation_data=(
                X_valid.reshape(X_valid.shape[0], X_valid.shape[1]),
                y_valid,
            ),
            callbacks=[es],
        )

        preds[i] = model.predict(
            X_valid.reshape(X_valid.shape[0], X_valid.shape[1])
        ).reshape(X_valid.shape[0], n_predict)

        if scaler:
            future_values = scaler.inverse_transform(
                model.predict(forecast_data_input.reshape(1, -1)).reshape(-1, 1)
            )
        else:
            future_values = model.predict(forecast_data_input.reshape(1, -1)).reshape(
                -1, 1
            )

        forecast_data[i] = future_values.flat

    forecast_data_df = pd.DataFrame(forecast_data.T, index=future_dates)
    return forecast_data_df, preds, y_valid, y_dates_valid, scaler


def rnn_model(
    data: Union[pd.Series, pd.DataFrame],
    n_input: int,
    n_predict: int,
    learning_rate: float,
    epochs: int,
    batch_size: int,
    test_size: float,
    n_loops: int,
    no_shuffle: bool,
) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, Any]:
    """Train RNN model on data based on config params

    Parameters
    ----------
    data : Union[pd.Series, pd.DataFrame]
        Data to fit
    n_input : int
        Length of input sequence
    n_predict : int
        Length of output to predict
    learning_rate : float
        Learning rate for optimizer
    epochs : int
        Number of training epochs
    batch_size : int
        Model batch size
    test_size : float
        Fraction of test size
    n_loops : int
        Number of loops to train model
    no_shuffle : bool
        Flag to not shuffle data

    Returns
    -------
    pd.DataFrame
        Dataframe of predictions
    np.array
        Array of validation predictions
    np.array
        Array of validation data
    np.array
        Array of validation x label data
    Any
        Scaler used for data
    """
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
    ) = prepare_scale_train_valid_test(
        data, n_input, n_predict, test_size, "", no_shuffle
    )
    if is_error:
        return pd.DataFrame(), np.array(0), np.array(0), np.array(0), None

    print(
        f"Training on {X_train.shape[0]} sequences of length {X_train.shape[1]}.  Using {X_valid.shape[0]} sequences "
        f" of length {X_valid.shape[1]} for validation. Model will run {n_loops} loops"
    )

    future_dates = get_next_stock_market_days(
        dates_forecast_input[-1], n_next_days=n_predict
    )

    preds = np.zeros((n_loops, X_valid.shape[0], n_predict))
    forecast_data = np.zeros((n_loops, n_predict))
    for i in range(n_loops):
        # Build Neural Network model
        model = build_neural_network_model(
            cfg_nn_models.Recurrent_Neural_Network,
            n_input,
            n_predict,
        )
        model.compile(
            optimizer=optimizers[cfg_nn_models.Optimizer](learning_rate=learning_rate),
            loss=cfg_nn_models.Loss,
        )
        model.fit(
            X_train.reshape(X_train.shape[0], X_train.shape[1], 1),
            y_train,
            epochs=epochs,
            verbose=True,
            batch_size=batch_size,
            validation_data=(
                X_valid.reshape(X_valid.shape[0], X_valid.shape[1], 1),
                y_valid,
            ),
            callbacks=[es],
        )

        preds[i] = model.predict(
            X_valid.reshape(X_valid.shape[0], X_valid.shape[1], 1)
        ).reshape(X_valid.shape[0], n_predict)

        forecast_data[i] = forecast(
            forecast_data_input, future_dates, model, scaler
        ).values.flat

    forecast_data_df = pd.DataFrame(forecast_data.T, index=future_dates)
    return forecast_data_df, preds, y_valid, y_dates_valid, scaler


def lstm_model(
    data: Union[pd.Series, pd.DataFrame],
    n_input: int,
    n_predict: int,
    learning_rate: float,
    epochs: int,
    batch_size: int,
    test_size: float,
    n_loops: int,
    no_shuffle: bool,
) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, Any]:
    """Train LSTM model on data based on config params

    Parameters
    ----------
    data : Union[pd.Series, pd.DataFrame]
        Data to fit
    n_input : int
        Length of input sequence
    n_predict : int
        Length of output to predict
    learning_rate : float
        Learning rate for optimizer
    epochs : int
        Number of training epochs
    batch_size : int
        Model batch size
    test_size : float
        Fraction of test size
    n_loops : int
        Number of loops to train model
    no_shuffle : bool
        Flag to not shuffle data

    Returns
    -------
    pd.DataFrame
        Dataframe of predictions
    np.array
        Array of validation predictions
    np.array
        Array of validation data
    np.array
        Array of validation x label data
    Any
        Scaler used for data
    """
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
    ) = prepare_scale_train_valid_test(
        data, n_input, n_predict, test_size, "", no_shuffle
    )
    if is_error:
        return pd.DataFrame(), np.array(0), np.array(0), np.array(0), None

    print(
        f"Training on {X_train.shape[0]} sequences of length {X_train.shape[1]}.  Using {X_valid.shape[0]} sequences "
        f" of length {X_valid.shape[1]} for validation. Model will run {n_loops} loops"
    )

    future_dates = get_next_stock_market_days(
        dates_forecast_input[-1], n_next_days=n_predict
    )

    preds = np.zeros((n_loops, X_valid.shape[0], n_predict))
    forecast_data = np.zeros((n_loops, n_predict))
    for i in range(n_loops):
        # Build Neural Network model
        model = build_neural_network_model(
            cfg_nn_models.Long_Short_Term_Memory,
            n_input,
            n_predict,
        )
        model.compile(
            optimizer=optimizers[cfg_nn_models.Optimizer](learning_rate=learning_rate),
            loss=cfg_nn_models.Loss,
        )
        model.fit(
            X_train.reshape(X_train.shape[0], X_train.shape[1], 1),
            y_train,
            epochs=epochs,
            verbose=True,
            batch_size=batch_size,
            validation_data=(
                X_valid.reshape(X_valid.shape[0], X_valid.shape[1], 1),
                y_valid,
            ),
            callbacks=[es],
        )

        preds[i] = model.predict(
            X_valid.reshape(X_valid.shape[0], X_valid.shape[1], 1)
        ).reshape(X_valid.shape[0], n_predict)

        forecast_data[i] = forecast(
            forecast_data_input, future_dates, model, scaler
        ).values.flat

    forecast_data_df = pd.DataFrame(forecast_data.T, index=future_dates)
    return forecast_data_df, preds, y_valid, y_dates_valid, scaler


def conv1d_model(
    data: Union[pd.Series, pd.DataFrame],
    n_input: int,
    n_predict: int,
    learning_rate: float,
    epochs: int,
    batch_size: int,
    test_size: float,
    n_loops: int,
    no_shuffle: bool,
) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray, Any]:
    """Train Conv1D model on data based on config params

    Parameters
    ----------
    data : Union[pd.Series, pd.DataFrame]
        Data to fit
    n_input : int
        Length of input sequence
    n_predict : int
        Length of output to predict
    learning_rate : float
        Learning rate for optimizer
    epochs : int
        Number of training epochs
    batch_size : int
        Model batch size
    test_size : float
        Fraction of test size
    n_loops : int
        Number of loops to train model
    no_shuffle : bool
        Flag to not shuffle data

    Returns
    -------
    pd.DataFrame
        Dataframe of predictions
    np.array
        Array of validation predictions
    np.array
        Array of validation data
    np.array
        Array of validation x label data
    Any
        Scaler used for data
    """
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
    ) = prepare_scale_train_valid_test(
        data, n_input, n_predict, test_size, "", no_shuffle
    )
    if is_error:
        return pd.DataFrame(), np.array(0), np.array(0), np.array(0), None

    print(
        f"Training on {X_train.shape[0]} sequences of length {X_train.shape[1]}.  Using {X_valid.shape[0]} sequences "
        f" of length {X_valid.shape[1]} for validation. Model will run {n_loops} loops"
    )

    future_dates = get_next_stock_market_days(
        dates_forecast_input[-1], n_next_days=n_predict
    )

    preds = np.zeros((n_loops, X_valid.shape[0], n_predict))
    forecast_data = np.zeros((n_loops, n_predict))
    for i in range(n_loops):
        # Build Neural Network model
        model = build_neural_network_model(
            cfg_nn_models.Convolutional,
            n_input,
            n_predict,
        )
        model.compile(
            optimizer=optimizers[cfg_nn_models.Optimizer](learning_rate=learning_rate),
            loss=cfg_nn_models.Loss,
        )
        model.fit(
            X_train.reshape(X_train.shape[0], X_train.shape[1], 1),
            y_train,
            epochs=epochs,
            verbose=True,
            batch_size=batch_size,
            validation_data=(
                X_valid.reshape(X_valid.shape[0], X_valid.shape[1], 1),
                y_valid,
            ),
            callbacks=[es],
        )

        preds[i] = model.predict(
            X_valid.reshape(X_valid.shape[0], X_valid.shape[1], 1)
        ).reshape(X_valid.shape[0], n_predict)

        forecast_data[i] = forecast(
            forecast_data_input, future_dates, model, scaler
        ).values.flat

    forecast_data_df = pd.DataFrame(forecast_data.T, index=future_dates)
    return forecast_data_df, preds, y_valid, y_dates_valid, scaler

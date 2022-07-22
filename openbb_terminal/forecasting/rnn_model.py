# pylint: disable=too-many-arguments
"""RNN Model"""
__docformat__ = "numpy"

import logging
from typing import Any, Tuple, Union, List


# import torch
# import torch.nn as nn
# import torch.optim as optim
import pandas as pd

from darts import TimeSeries
from darts.models import RNNModel
from darts.utils.likelihood_models import GaussianLikelihood
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecasting import helpers

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_rnn_data(
    data: Union[pd.Series, pd.DataFrame],
    n_predict: int = 5,
    target_col: str = "close",
    train_split: float = 0.85,
    forecast_horizon: int = 5,
    model_type: str = "LSTM",
    hidden_dim: int = 20,
    dropout: float = 0.0,
    batch_size: int = 16,
    n_epochs: int = 100,
    learning_rate: float = 1e-3,
    model_save_name: str = "rnn_model",
    training_length: int = 20,
    input_chunk_size: int = 14,
    force_reset: bool = True,
    save_checkpoints: bool = True,
) -> Tuple[List[TimeSeries], List[TimeSeries], List[TimeSeries], float, Any]:
    """Perform RNN forecasting

    Args:
        data (Union[pd.Series, pd.DataFrame]):
            Input Data
        n_predict (int, optional):
            Days to predict. Defaults to 5.
        target_col (str, optional):
            Target column to forecast. Defaults to "close".
        train_split (float, optional):
            Train/val split. Defaults to 0.85.
        forecast_horizon (int, optional):
            Forecast horizon when performing historical forecasting. Defaults to 5.
        model_type (str, optional):
            Either a string specifying the RNN module type ("RNN", "LSTM" or "GRU"). Defaults to "LSTM".
        hidden_dim (int, optional):
            Size for feature maps for each hidden RNN layer.. Defaults to 20.
        dropout (float, optional):
            Fraction of neurons afected by Dropout. Defaults to 0.0.
        batch_size (int, optional):
            Number of time series (input and output sequences) used in each training pass. Defaults to 32.
        n_epochs (int, optional):
            Number of epochs over which to train the model. Defaults to 100.
        learning_rate (float, optional):
            Defaults to 1e-3.
        model_save_name (str, optional):
            Name for model. Defaults to "brnn_model".
        force_reset (bool, optional):
            If set to True, any previously-existing model with the same name will be reset
            (all checkpoints will be discarded). Defaults to True.
        save_checkpoints (bool, optional):
            Whether or not to automatically save the untrained model and checkpoints from training.
            Defaults to True.

    Returns:
        List[TimeSeries]
            Adjusted Data series
        List[TimeSeries]
            Historical forecast by best RNN model
        List[TimeSeries]
            list of Predictions
        float
            Mean average precision error
        Any
            Best RNN Model
    """

    # TODO add proper doc string
    # TODO Check if torch GPU AVAILABLE
    # TODO add in covariates
    # todo add in all possible parameters for training - RNN does not take past covariates
    # Export model / save
    # load trained model

    # Target Timeseries
    # TODO Check if torch GPU AVAILABLE

    use_scalers = True
    probabilistic = True
    past_covariates = None
    past_covariate_whole = None

    _, scaler, ticker_series = helpers.get_series(
        data, target_col, is_scaler=use_scalers
    )
    train, val = ticker_series.split_before(train_split)

    rnn_model = RNNModel(
        model=model_type,
        hidden_dim=hidden_dim,
        dropout=dropout,
        batch_size=batch_size,
        n_epochs=n_epochs,
        optimizer_kwargs={"lr": learning_rate},
        model_name=model_save_name,
        random_state=42,
        training_length=training_length,
        input_chunk_length=input_chunk_size,
        pl_trainer_kwargs=helpers.get_pl_kwargs(
            patience=5, monitor="val_loss", accelerator="cpu"
        ),
        force_reset=force_reset,
        save_checkpoints=save_checkpoints,
        likelihood=GaussianLikelihood(),
    )

    # fit model on train series for historical forecasting
    helpers.fit_model(rnn_model, train, val)
    best_model = RNNModel.load_from_checkpoint(model_name=model_save_name, best=True)

    # Showing historical backtesting without retraining model (too slow)
    return helpers.get_prediction(
        "RNN",
        probabilistic,
        use_scalers,
        scaler,
        past_covariates,
        best_model,
        ticker_series,
        past_covariate_whole,
        train_split,
        forecast_horizon,
        n_predict,
    )

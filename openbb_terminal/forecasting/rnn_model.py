# pylint: disable=too-many-arguments
"""RNN Model"""
__docformat__ = "numpy"

import logging
from typing import Any, Tuple, Union, List


# import torch
# import torch.nn as nn
# import torch.optim as optim
import numpy as np
import pandas as pd

from darts import TimeSeries
from darts.models import RNNModel
from darts.dataprocessing.transformers import MissingValuesFiller, Scaler
from darts.utils.likelihood_models import GaussianLikelihood
from darts.metrics import mape
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from openbb_terminal.decorators import log_start_end

from openbb_terminal.rich_config import console

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
            If set to True, any previously-existing model with the same name will be reset (all checkpoints will be discarded). Defaults to True.
        save_checkpoints (bool, optional):
            Whether or not to automatically save the untrained model and checkpoints from training. Defaults to True.

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

    filler = MissingValuesFiller()
    scaler = Scaler()

    # TODO add proper doc string
    # TODO Check if torch GPU AVAILABLE
    # TODO add in covariates
    # todo add in all possible parameters for training - RNN does not take past covariates
    # Export model / save
    # load trained model

    # Target Timeseries
    scaled_ticker_series = scaler.fit_transform(
        filler.transform(
            TimeSeries.from_dataframe(
                data,
                time_col="date",
                value_cols=[target_col],
                freq="B",
                fill_missing_dates=True,
            )
        )
    ).astype(np.float32)

    scaled_train, scaled_val = scaled_ticker_series.split_before(train_split)

    # --------------------------------------------------
    # Early Stopping
    my_stopper = EarlyStopping(
        monitor="val_loss",
        patience=5,
        min_delta=0,
        mode="min",
    )
    pl_trainer_kwargs = {"callbacks": [my_stopper], "accelerator": "cpu"}

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
        pl_trainer_kwargs=pl_trainer_kwargs,
        force_reset=force_reset,
        save_checkpoints=save_checkpoints,
        likelihood=GaussianLikelihood(),
    )

    # fit model on train series for historical forecasting
    rnn_model.fit(
        series=scaled_train,
        val_series=scaled_val,
    )
    best_model = RNNModel.load_from_checkpoint(model_name=model_save_name, best=True)

    # Showing historical backtesting without retraining model (too slow)
    scaled_historical_fcast = best_model.historical_forecasts(
        scaled_ticker_series,
        start=train_split,
        forecast_horizon=forecast_horizon,
        retrain=False,
        verbose=True,
        num_samples=500,
    )

    # Predict N timesteps in the future
    scaled_prediction = best_model.predict(
        series=scaled_ticker_series, n=n_predict, num_samples=500
    )

    precision = mape(
        actual_series=scaled_ticker_series, pred_series=scaled_historical_fcast
    )  # mape = mean average precision error
    console.print(f"RNN model obtains MAPE: {precision:.2f}% \n")

    # scale back
    ticker_series = scaler.inverse_transform(scaled_ticker_series)
    historical_fcast = scaler.inverse_transform(scaled_historical_fcast)
    prediction = scaler.inverse_transform(scaled_prediction)

    return (
        ticker_series,
        historical_fcast,
        prediction,
        precision,
        best_model,
    )

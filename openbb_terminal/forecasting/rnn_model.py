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
    past_covariates: str = None,
    train_split: float = 0.85,
    forecast_horizon: int = 3,
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

    """Performs Recurrent Neural Network Forcasting forecasting

    Parameters
    ----------
    data : Union[pd.Series, np.ndarray]
        Input data.
    n_predict: int
        Number of days to forecast
    start_window: float
        Size of sliding window from start of timeseries and onwards
    forecast_horizon: int
        Number of days to forecast when backtesting and retraining historical

    Returns
    -------
    List[TimeSeries]
        Adjusted Data series
    List[TimeSeries]
        Historical forecast by best theta
    List[TimeSeries]
        list of Predictions
    float
        Mean average precision error
    float
        Best Theta
    Any
        Theta Model
    """
    filler = MissingValuesFiller()
    scaler = Scaler()

    # TODO add proper doc string
    # TODO Check if torch GPU AVAILABLE
    # TODO add in covariates
    # todo add in all possible parameters for training
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

    scaled_train, scaled_val = scaled_ticker_series.split_before(float(train_split))

    # --------------------------------------------------
    # Covariates
    # TODO make this a for loop for multiple covariates
    scaled_covariates_whole = None
    covariates_scalers = []

    # split covariates by name filering out commas
    target_covariates_names = past_covariates.split(",")

    for column in target_covariates_names:
        console.print(f"[green]Covariate: {column}[/green]")
        _temp_scaler = Scaler()
        covariates_scalers.append(_temp_scaler)
        _temp_new_scaled_covariate = _temp_scaler.fit_transform(
            filler.transform(
                TimeSeries.from_dataframe(
                    data,
                    time_col="date",
                    value_cols=[column],
                    freq="B",
                    fill_missing_dates=True,
                )
            )
        ).astype(np.float32)

        # continually stack covariates based on column names
        scaled_covariates_whole = scaled_covariates_whole.stack(
            _temp_new_scaled_covariate
        )

    # Split the full scale covariate to train and val
    scaled_covariate_train, scaled_covariate_val = scaled_covariates_whole.split_before(
        float(train_split)
    )

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
    )

    # fit model on train series for historical forecasting
    rnn_model.fit(
        series=scaled_train,
        val_series=scaled_val,
        past_covariates=scaled_covariate_train,
        val_past_covariates=scaled_covariate_val,
    )
    best_model = RNNModel.load_from_checkpoint(model_name="rnn_model", best=True)

    # Showing historical backtesting without retraining model (too slow)
    scaled_historical_fcast = rnn_model.historical_forecasts(
        scaled_ticker_series,
        start=float(train_split),
        forecast_horizon=int(forecast_horizon),
        retrain=False,
        verbose=True,
    )

    # Predict N timesteps in the future
    scaled_prediction = best_model.predict(
        series=scaled_ticker_series,
        n=int(n_predict, past_covariates=scaled_covariates_whole),
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
        rnn_model,
    )

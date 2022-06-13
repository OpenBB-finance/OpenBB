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
from darts.models import BlockRNNModel
from darts.dataprocessing.transformers import MissingValuesFiller, Scaler
from darts.utils.likelihood_models import GaussianLikelihood
from darts.metrics import mape
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from openbb_terminal.decorators import log_start_end

from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_brnn_data(
    data: Union[pd.Series, pd.DataFrame],
    n_predict: int = 5,
    target_col: str = "close",
    train_split: float = 0.85,
    past_covariates: str = None,
    forecast_horizon: int = 5,
    input_chunk_length: int = 14,
    output_chunk_length: int = 5,
    model_type: str = "LSTM",
    n_rnn_layers: int = 1,
    hidden_size: int = 20,
    dropout: float = 0.0,
    batch_size: int = 32,
    n_epochs: int = 100,
    learning_rate: float = 1e-3,
    model_save_name: str = "brnn_model",
    force_reset: bool = True,
    save_checkpoints: bool = True,
) -> Tuple[List[TimeSeries], List[TimeSeries], List[TimeSeries], float, Any]:
    """Performs Block RNN forecasting

    Args:
        data (Union[pd.Series, pd.DataFrame]):
            Input Data
        n_predict (int, optional):
            Days to predict. Defaults to 5.
        target_col (str, optional):
            Target column to forecast. Defaults to "close".
        train_split (float, optional):
            Train/val split. Defaults to 0.85.
        past_covariates (str, optional):
            Multiple secondary columns to factor in when forecasting. Defaults to None.
        forecast_horizon (int, optional):
            Forecast horizon when performing historical forecasting. Defaults to 5.
        input_chunk_length (int, optional):
            Number of past time steps that are fed to the forecasting module at prediction time. Defaults to 14.
        output_chunk_length (int, optional):
            The length of the forecast of the model. Defaults to 5.
        model_type (str, optional):
            Either a string specifying the RNN module type ("RNN", "LSTM" or "GRU"). Defaults to "LSTM".
        n_rnn_layers (int, optional):
             Number of layers in the RNN module. Defaults to 1.
        hidden_size (int, optional):
            Size for feature maps for each hidden RNN layer. Defaults to 20.
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
            Best BRNN Model
    """

    filler = MissingValuesFiller()
    scaler = Scaler()

    # TODO Check if torch GPU AVAILABLE

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
    if past_covariates is not None:
        covariates_scalers = []  # to hold all temp scalers in case we need them
        target_covariates_names = past_covariates.split(",")

        # create first covariate to then stack onto
        past_covariate_scaler = Scaler()
        console.print(f"[green]Covariate #0: {target_covariates_names[0]}[/green]")
        scaled_past_covariate_whole = past_covariate_scaler.fit_transform(
            filler.transform(
                TimeSeries.from_dataframe(
                    data,
                    time_col="date",
                    value_cols=target_covariates_names[0],
                    freq="B",
                    fill_missing_dates=True,
                )
            )
        ).astype(np.float32)

        if len(target_covariates_names) > 1:
            for i, column in enumerate(target_covariates_names[1:]):
                console.print(f"[green]Covariate #{i+1}: {column}[/green]")
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
                scaled_past_covariate_whole = scaled_past_covariate_whole.stack(
                    _temp_new_scaled_covariate
                )

        # Split the full scale covariate to train and val
        (
            scaled_past_covariate_train,
            scaled_past_covariate_val,
        ) = scaled_past_covariate_whole.split_before(train_split)

    # --------------------------------------------------
    # Early Stopping
    my_stopper = EarlyStopping(
        monitor="val_loss",
        patience=5,
        min_delta=0,
        mode="min",
    )
    pl_trainer_kwargs = {"callbacks": [my_stopper], "accelerator": "cpu"}

    brnn_model = BlockRNNModel(
        input_chunk_length=input_chunk_length,
        output_chunk_length=output_chunk_length,
        model=model_type,
        n_rnn_layers=n_rnn_layers,
        hidden_size=hidden_size,
        dropout=dropout,
        batch_size=batch_size,
        n_epochs=n_epochs,
        optimizer_kwargs={"lr": learning_rate},
        model_name=model_save_name,
        random_state=42,
        pl_trainer_kwargs=pl_trainer_kwargs,
        force_reset=force_reset,
        save_checkpoints=save_checkpoints,
        likelihood=GaussianLikelihood(),
    )

    # fit model on train series for historical forecasting
    if past_covariates is not None:
        brnn_model.fit(
            series=scaled_train,
            val_series=scaled_val,
            past_covariates=scaled_past_covariate_train,
            val_past_covariates=scaled_past_covariate_val,
        )
    else:
        brnn_model.fit(
            series=scaled_train,
            val_series=scaled_val,
        )
    best_model = BlockRNNModel.load_from_checkpoint(
        model_name=model_save_name, best=True
    )

    # Showing historical backtesting without retraining model (too slow)
    if past_covariates is not None:
        scaled_historical_fcast = best_model.historical_forecasts(
            scaled_ticker_series,
            past_covariates=scaled_past_covariate_whole,
            start=train_split,
            forecast_horizon=forecast_horizon,
            retrain=False,
            verbose=True,
        )
    else:
        scaled_historical_fcast = best_model.historical_forecasts(
            scaled_ticker_series,
            start=train_split,
            forecast_horizon=forecast_horizon,
            retrain=False,
            verbose=True,
        )

    # Predict N timesteps in the future
    if past_covariates is not None:
        scaled_prediction = best_model.predict(
            series=scaled_ticker_series,
            past_covariates=scaled_past_covariate_whole,
            n=n_predict,
        )
    else:
        scaled_prediction = best_model.predict(series=scaled_ticker_series, n=n_predict)

    precision = mape(
        actual_series=scaled_ticker_series, pred_series=scaled_historical_fcast
    )  # mape = mean average precision error
    console.print(f"BRNN model obtains MAPE: {precision:.2f}% \n")

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

# pylint: disable=too-many-arguments
"""TCN Model"""
__docformat__ = "numpy"

import logging
from typing import Any, Tuple, Union, List


# import torch
# import torch.nn as nn
# import torch.optim as optim
import numpy as np
import pandas as pd

from darts import TimeSeries
from darts.models import TCNModel
from darts.dataprocessing.transformers import MissingValuesFiller, Scaler
from darts.metrics import mape
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecasting import helpers

from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_tcn_data(
    data: Union[pd.Series, pd.DataFrame],
    n_predict: int = 5,
    target_col: str = "close",
    past_covariates: str = None,
    train_split: float = 0.85,
    forecast_horizon: int = 5,
    input_chunk_length: int = 14,
    output_chunk_length: int = 5,
    dropout: float = 0.1,
    num_filters: int = 6,
    weight_norm: bool = True,
    dilation_base: int = 2,
    n_epochs: int = 100,
    learning_rate: float = 1e-3,
    batch_size: int = 800,
    model_save_name: str = "tcn_model",
    force_reset: bool = True,
    save_checkpoints: bool = True,
) -> Tuple[List[TimeSeries], List[TimeSeries], List[TimeSeries], float, Any]:
    """Perform TCN forecasting

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
        dropout (float, optional):
            Fraction of neurons afected by Dropout. Defaults to 0.1.
        num_filters (int, optional):
            The number of filters in a convolutional layer of the TCN. Defaults to 6.
        weight_norm (bool, optional):
            Boolean value indicating whether to use weight normalization. Defaults to True.
        dilation_base (int, optional):
            The base of the exponent that will determine the dilation on every level. Defaults to 2.
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
            Best TCN Model
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

    (
        scaled_past_covariate_whole,
        scaled_past_covariate_train,
        scaled_past_covariate_val,
    ) = helpers.scaled_past_covs(past_covariates, filler, data, train_split)

    my_stopper = helpers.early_stopper(10)

    pl_trainer_kwargs = {"callbacks": [my_stopper], "accelerator": "cpu"}

    tcn_model = TCNModel(
        input_chunk_length=input_chunk_length,
        output_chunk_length=output_chunk_length,
        dropout=dropout,
        dilation_base=dilation_base,
        weight_norm=weight_norm,
        num_filters=num_filters,
        n_epochs=n_epochs,
        nr_epochs_val_period=1,
        batch_size=batch_size,
        optimizer_kwargs={"lr": learning_rate},
        model_name=model_save_name,
        force_reset=force_reset,
        save_checkpoints=save_checkpoints,
        random_state=42,
        pl_trainer_kwargs=pl_trainer_kwargs,
    )

    # fit model on train series for historical forecasting
    if past_covariates is not None:
        tcn_model.fit(
            series=scaled_train,
            val_series=scaled_val,
            past_covariates=scaled_past_covariate_train,
            val_past_covariates=scaled_past_covariate_val,
        )
    else:
        tcn_model.fit(
            series=scaled_train,
            val_series=scaled_val,
        )
    best_model = TCNModel.load_from_checkpoint(model_name=model_save_name, best=True)

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

    if past_covariates is not None:
        # Predict N timesteps in the future
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
    console.print(f"TCN model obtains MAPE: {precision:.2f}% \n")

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

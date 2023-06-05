"""Temporal Fusion Transformer View"""
__docformat__ = "numpy"

import logging
from datetime import datetime
from typing import Optional, Union

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecast import helpers, tft_model

logger = logging.getLogger(__name__)
# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def display_tft_forecast(
    data: Union[pd.Series, pd.DataFrame],
    target_column: str = "close",
    dataset_name: str = "",
    n_predict: int = 5,
    past_covariates: Optional[str] = None,
    train_split: float = 0.85,
    forecast_horizon: int = 5,
    input_chunk_length: int = 14,
    output_chunk_length: int = 5,
    hidden_size: int = 16,
    lstm_layers: int = 1,
    num_attention_heads: int = 4,
    full_attention: bool = False,
    dropout: float = 0.1,
    hidden_continuous_size: int = 8,
    n_epochs: int = 200,
    batch_size: int = 32,
    model_save_name: str = "tft_model",
    force_reset: bool = True,
    save_checkpoints: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
    residuals: bool = False,
    forecast_only: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    naive: bool = False,
    export_pred_raw: bool = False,
    metric: str = "mape",
    external_axes: bool = False,
):
    """Display Temporal Fusion Transformer forecast

    Parameters
    ----------
    data (Union[pd.Series, pd.DataFrame]):
        Input Data
    target_column: Optional[str]:
        Target column to forecast. Defaults to "close".
    dataset_name str
        The name of the ticker to be predicted
    n_predict (int, optional):
        Days to predict. Defaults to 5.
    train_split (float, optional):
        Train/val split. Defaults to 0.85.
    past_covariates (str, optional):
        Multiple secondary columns to factor in when forecasting. Defaults to None.
    forecast_horizon (int, optional):
        Forecast horizon when performing historical forecasting. Defaults to 5.
    input_chunk_length (int, optional):
        Number of past time steps that are fed to the forecasting module at prediction time.
        Defaults to 14.
    output_chunk_length (int, optional):
        The length of the forecast of the model. Defaults to 5.
    hidden_size (int, optional):
        Hidden state size of the TFT. Defaults to 16.
    lstm_layers (int, optional):
        Number of layers for the Long Short Term Memory Encoder and Decoder. Defaults to 16.
    num_attention_headers (int, optional):
        Number of attention heads. Defaults to 4.
    full_attention (bool, optional):
        Whether to apply a multi-head attention query. Defaults to False>
    dropout (float, optional):
        Fraction of neurons affected by dropout. Defaults to 0.1.
    hidden_continuous_size (int, optional):
        Default hidden size for processing continuous variables. Defaults to 8.
    n_epochs (int, optional):
        Number of epochs to run during training. Defaults to 200.
    batch_size (int, optional):
        Number of samples to pass through network during a single epoch. Defaults to 32.
    model_save_name (str, optional):
        The name for the model. Defaults to tft_model
    force_reset (bool, optional):
        If set to True, any previously-existing model with the same name will be reset
        (all checkpoints will be discarded). Defaults to True.
    save_checkpoints (bool, optional):
        Whether or not to automatically save the untrained model and checkpoints from training.
        Defaults to True.
    residuals: bool
        Whether to show residuals for the model. Defaults to False.
    forecast_only: bool
        Whether to only show dates in the forecasting range. Defaults to False.
    start_date: Optional[datetime]
        The starting date to perform analysis, data before this is trimmed. Defaults to None.
    end_date: Optional[datetime]
        The ending date to perform analysis, data after this is trimmed. Defaults to None.
    naive: bool
        Whether to show the naive baseline. This just assumes the closing price will be the same
        as the previous day's closing price. Defaults to False.
    metric: str
        The metric to use for the model. Defaults to "mape".
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    data = helpers.clean_data(
        data, start_date, end_date, target_column, past_covariates
    )
    if not helpers.check_data(data, target_column, past_covariates):
        return None
    output_chunk_length = helpers.check_output(
        output_chunk_length, n_predict, bool(past_covariates)
    )
    (
        ticker_series,
        historical_fcast,
        predicted_values,
        precision,
        _model,
    ) = tft_model.get_tft_data(
        data=data,
        n_predict=n_predict,
        target_column=target_column,
        past_covariates=past_covariates,
        train_split=train_split,
        forecast_horizon=forecast_horizon,
        input_chunk_length=input_chunk_length,
        output_chunk_length=output_chunk_length,
        hidden_size=hidden_size,
        lstm_layers=lstm_layers,
        num_attention_heads=num_attention_heads,
        full_attention=full_attention,
        dropout=dropout,
        hidden_continuous_size=hidden_continuous_size,
        n_epochs=n_epochs,
        batch_size=batch_size,
        model_save_name=model_save_name,
        force_reset=force_reset,
        save_checkpoints=save_checkpoints,
        metric=metric,
    )
    if ticker_series == []:
        return None

    probabilistic = True
    fig = helpers.plot_forecast(
        name="TFT",
        target_col=target_column,
        historical_fcast=historical_fcast,
        predicted_values=predicted_values,
        ticker_series=ticker_series,
        ticker_name=dataset_name,
        data=data,
        n_predict=n_predict,
        forecast_horizon=forecast_horizon,
        past_covariates=past_covariates,
        precision=precision,
        probabilistic=probabilistic,
        export=export,
        sheet_name=sheet_name,
        forecast_only=forecast_only,
        naive=naive,
        export_pred_raw=export_pred_raw,
        metric=metric,
        external_axes=external_axes,
    )
    if residuals:
        helpers.plot_residuals(
            _model, past_covariates, ticker_series, forecast_horizon=forecast_horizon
        )

    return fig

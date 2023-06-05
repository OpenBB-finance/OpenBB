"""NBEATS View"""
__docformat__ = "numpy"

import logging
from datetime import datetime
from typing import Optional, Union

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecast import helpers, nbeats_model

logger = logging.getLogger(__name__)
# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def display_nbeats_forecast(
    data: Union[pd.DataFrame, pd.Series],
    target_column: str = "close",
    dataset_name: str = "",
    n_predict: int = 5,
    past_covariates: Optional[str] = None,
    train_split: float = 0.85,
    forecast_horizon: int = 5,
    input_chunk_length: int = 14,
    output_chunk_length: int = 5,
    num_stacks: int = 10,
    num_blocks: int = 3,
    num_layers: int = 4,
    layer_widths: int = 512,
    n_epochs: int = 300,
    learning_rate: float = 1e-3,
    batch_size: int = 800,
    model_save_name: str = "nbeats_model",
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
    """Display NBEATS forecast

    Parameters
    ----------
    data: Union[pd.Series, pd.DataFrame]
        Input Data
    target_column: str
        Target column to forecast. Defaults to "close".
    dataset_name: str
        The name of the ticker to be predicted
    n_predict: int
        Days to predict. Defaults to 5.
    train_split: float
        Train/val split. Defaults to 0.85.
    past_covariates: str
        Multiple secondary columns to factor in when forecasting. Defaults to None.
    forecast_horizon: int
        Forecast horizon when performing historical forecasting. Defaults to 5.
    input_chunk_length: int
        Number of past time steps that are fed to the forecasting module at prediction time. Defaults to 14.
    output_chunk_length: int
        The length of the forecast of the model. Defaults to 5.
    num_stacks: int
        The number of stacks that make up the whole model. Defaults to 10.
    num_blocks: int
        The number of blocks making up every stack. Defaults to 3.
    num_layers: int
        The number of fully connected layers preceding the final forking layers in each block
        of every stack. Defaults to 4.
    layer_widths: int
        Determines the number of neurons that make up each fully connected layer in each block
        of every stack. Defaults to 512.
    batch_size: int
        Number of time series (input and output sequences) used in each training pass. Defaults
        to 32.
    n_epochs: int
        Number of epochs over which to train the model. Defaults to 100.
    learning_rate: float
        Defaults to 1e-3.
    model_save_name: str
        Name for model. Defaults to "brnn_model".
    force_reset: bool
        If set to True, any previously-existing model with the same name will be reset (all
        checkpoints will be discarded). Defaults to True.
    save_checkpoints: bool
        Whether or not to automatically save the untrained model and checkpoints from training.
        Defaults to True.
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
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
    export_pred_raw: bool
        Whether to export the raw predicted values. Defaults to False.
    metric: str
        Metric to use for evaluation. Defaults to "mape".
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
    ) = nbeats_model.get_NBEATS_data(
        data=data,
        n_predict=n_predict,
        target_column=target_column,
        past_covariates=past_covariates,
        train_split=train_split,
        forecast_horizon=forecast_horizon,
        input_chunk_length=input_chunk_length,
        output_chunk_length=output_chunk_length,
        num_stacks=num_stacks,
        num_blocks=num_blocks,
        num_layers=num_layers,
        layer_widths=layer_widths,
        batch_size=batch_size,
        n_epochs=n_epochs,
        learning_rate=learning_rate,
        model_save_name=model_save_name,
        force_reset=force_reset,
        save_checkpoints=save_checkpoints,
        metric=metric,
    )
    if ticker_series == []:
        return None

    probabilistic = False
    fig = helpers.plot_forecast(
        name="NBEATS",
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

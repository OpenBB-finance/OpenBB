"""Block RNN View"""
__docformat__ = "numpy"

import logging
from datetime import datetime
from typing import Optional, Union

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forecast import brnn_model, helpers

logger = logging.getLogger(__name__)
# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def display_brnn_forecast(
    data: Union[pd.Series, pd.DataFrame],
    target_column: str = "close",
    dataset_name: str = "",
    n_predict: int = 5,
    past_covariates: Optional[str] = None,
    train_split: float = 0.85,
    forecast_horizon: int = 5,
    input_chunk_length: int = 14,
    output_chunk_length: int = 5,
    model_type: str = "LSTM",
    n_rnn_layers: int = 1,
    dropout: float = 0.0,
    batch_size: int = 32,
    n_epochs: int = 100,
    learning_rate: float = 1e-3,
    model_save_name: str = "brnn_model",
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
) -> Union[OpenBBFigure, None]:
    """Display BRNN forecast

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
        model_type: str
            Either a string specifying the RNN module type ("RNN", "LSTM" or "GRU"). Defaults to "LSTM".
        n_rnn_layers: int
                Number of layers in the RNN module. Defaults to 1.
        dropout: float
            Fraction of neurons affected by Dropout. Defaults to 0.0.
        batch_size: int
            Number of time series (input and output sequences) used in each training pass. Defaults to 32.
        n_epochs: int
            Number of epochs over which to train the model. Defaults to 101.
        learning_rate: float
            Defaults to 1e-3.
        model_save_name: str
            Name for model. Defaults to "brnn_model".
        force_reset: bool
            If set to True, any previously-existing model with the same name will be reset
            (all checkpoints will be discarded). Defaults to True.
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
    <<<<<<< HEAD
        external_axes : bool, optional
            Whether to return the figure object or not, by default False
    =======
        export_pred_raw: bool
            Whether to export the raw predicted values. Defaults to False.
        metric: str
            The metric to use for the model. Defaults to "mape".
        external_axes: Optional[List[plt.axes]]
            External axes to plot on
    >>>>>>> OpenBBTerminal-main
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
    ) = brnn_model.get_brnn_data(
        data=data,
        n_predict=n_predict,
        target_column=target_column,
        past_covariates=past_covariates,
        train_split=train_split,
        forecast_horizon=forecast_horizon,
        input_chunk_length=input_chunk_length,
        output_chunk_length=output_chunk_length,
        model_type=model_type,
        n_rnn_layers=n_rnn_layers,
        dropout=dropout,
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
        name="BRNN",
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

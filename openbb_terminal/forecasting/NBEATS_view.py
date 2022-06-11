"""NBEATS View"""
__docformat__ = "numpy"

import logging
import os
from typing import Union

import matplotlib.pyplot as plt
import pandas as pd

from openbb_terminal.config_terminal import theme
from openbb_terminal.forecasting import NBEATS_model
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
)
from openbb_terminal.rich_config import console
from openbb_terminal.common.prediction_techniques.pred_helper import (
    print_pretty_prediction,
)

logger = logging.getLogger(__name__)
# pylint: disable=too-many-arguments


def dt_format(x):
    """Convert any Timestamp to YYYY-MM-DD
    Args:
        x: Pandas Timestamp of any length
    Returns:
        x: formatted string
    """
    # convert string to pandas datetime
    x = pd.to_datetime(x)
    x = x.strftime("%Y-%m-%d")
    return x


@log_start_end(log=logger)
def display_nbeats_forecast(
    data: Union[pd.DataFrame, pd.Series],
    ticker_name: str,
    n_predict: int = 5,
    target_col: str = "close",
    past_covariates: str = None,
    train_split: float = 0.85,
    forecast_horizon: int = 3,
    input_chunk_length: int = 30,
    output_chunk_length: int = 7,
    num_stacks: int = 10,
    num_blocks: int = 3,
    num_layers: int = 4,
    layer_widths: int = 512,
    n_epochs: int = 100,
    learning_rate: float = 1e-3,
    batch_size: int = 800,
    model_save_name: str = "nbeats_model",
    force_reset: bool = True,
    save_checkpoints: bool = True,
    export: str = "",
):
    """Display NBEATS forecast

    Parameters
    ----------
    data : Union[pd.Series, np.array]
        Data to forecast
    n_predict: int
        Number of days to forecast
    start_window: float
        Size of sliding window from start of timeseries and onwards
    forecast_horizon: int
        Number of days to forecast when backtesting and retraining historical
    export: str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axis is expected in the list), by default None
    """

    # reformat the date column to remove any hour/min/sec
    data["date"] = data["date"].apply(dt_format)

    (
        ticker_series,
        historical_fcast,
        predicted_values,
        precision,
        _model,
    ) = NBEATS_model.get_NBEATS_data(
        data,
        n_predict,
        target_col,
        past_covariates,
        train_split,
        forecast_horizon,
        input_chunk_length,
        output_chunk_length,
        num_stacks,
        num_blocks,
        num_layers,
        layer_widths,
        batch_size,
        n_epochs,
        learning_rate,
        model_save_name,
        force_reset,
        save_checkpoints,
    )
    # Plotting with Matplotlib
    external_axes = None
    if not external_axes:
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item.\n[/red]")
            return
        ax = external_axes

    # ax = fig.get_axes()[0] # fig gives list of axes (only one for this case)
    ticker_series.plot(label=target_col, figure=fig)
    historical_fcast.plot(
        label=f"Backtest {forecast_horizon}-Steps ahead forecast",
        figure=fig,
    )
    predicted_values.plot(
        label=f"NBEATS Forecast w/ past covs({past_covariates})", figure=fig
    )
    ax.set_title(
        f"NBEATS for ${ticker_name} for next [{n_predict}] days (MAPE={precision:.2f}%)"
    )
    ax.set_ylabel(target_col)
    ax.set_xlabel("Date")
    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    numeric_forecast = predicted_values.pd_dataframe()[target_col].tail(n_predict)
    print_pretty_prediction(numeric_forecast, data[target_col].iloc[-1])

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "expo")

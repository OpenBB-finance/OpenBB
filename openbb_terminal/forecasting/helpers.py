import logging
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from darts.dataprocessing.transformers import Scaler
from darts import TimeSeries
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from openbb_terminal.rich_config import console
from openbb_terminal.config_terminal import theme
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
)
from openbb_terminal.common.prediction_techniques.pred_helper import (
    print_pretty_prediction,
)
from openbb_terminal.config_plot import PLOT_DPI

logger = logging.getLogger(__name__)


def scaled_past_covs(past_covariates, filler, data, train_split):
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
        return (
            scaled_past_covariate_whole,
            scaled_past_covariate_train,
            scaled_past_covariate_val,
        )


def early_stopper(patience: int):
    my_stopper = EarlyStopping(
        monitor="val_loss",
        patience=patience,
        min_delta=0,
        mode="min",
    )
    return my_stopper


def plot_forecast(
    name: str,
    target_col: str,
    historical_fcast,
    predicted_values,
    ticker_series,
    ticker_name: str,
    data,
    n_predict: int,
    forecast_horizon,
    past_covariates,
    precision,
    export: str,
    low_quantile: float = None,
    high_quantile: float = None,
):
    quant_kwargs = {}
    if low_quantile:
        quant_kwargs["low_quantile"] = low_quantile
    if high_quantile:
        quant_kwargs["high_quantile"] = high_quantile
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
        **quant_kwargs,
    )

    pred_label = f"{name} Forecast"
    if past_covariates:
        pred_label += f" w/ past covs({past_covariates})"
    predicted_values.plot(label=pred_label, figure=fig, **quant_kwargs)
    ax.set_title(
        f"{name} for ${ticker_name} for next [{n_predict}] days (MAPE={precision:.2f}%)"
    )
    ax.set_ylabel(target_col)
    ax.set_xlabel("Date")
    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()

    numeric_forecast = predicted_values.pd_dataframe()[target_col].tail(n_predict)
    print_pretty_prediction(numeric_forecast, data[target_col].iloc[-1])

    export_data(export, os.path.dirname(os.path.abspath(__file__)), "expo")


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

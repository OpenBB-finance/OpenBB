# pylint: disable=too-many-arguments
import os
import argparse
from typing import Dict, Any
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from darts.dataprocessing.transformers import MissingValuesFiller, Scaler
from darts.utils.statistics import plot_residuals_analysis
from darts import TimeSeries
from darts.metrics import mape
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


def past_covs(past_covariates, filler, data, train_split, is_scaler=True):
    if past_covariates is not None:
        covariates_scalers = []  # to hold all temp scalers in case we need them
        target_covariates_names = past_covariates.split(",")

        # create first covariate to then stack onto
        console.print(f"[green]Covariate #0: {target_covariates_names[0]}[/green]")
        if is_scaler:
            past_covariate_scaler = Scaler()
            past_covariate_whole = past_covariate_scaler.fit_transform(
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
        else:
            past_covariate_whole = filler.transform(
                TimeSeries.from_dataframe(
                    data,
                    time_col="date",
                    value_cols=target_covariates_names[0],
                    freq="B",
                    fill_missing_dates=True,
                )
            ).astype(np.float32)

        if len(target_covariates_names) > 1:
            for i, column in enumerate(target_covariates_names[1:]):
                console.print(f"[green]Covariate #{i+1}: {column}[/green]")
                if is_scaler:
                    _temp_scaler = Scaler()
                    covariates_scalers.append(_temp_scaler)
                    _temp_new_covariate = _temp_scaler.fit_transform(
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
                else:
                    _temp_new_covariate = filler.transform(
                        TimeSeries.from_dataframe(
                            data,
                            time_col="date",
                            value_cols=[column],
                            freq="B",
                            fill_missing_dates=True,
                        )
                    ).astype(np.float32)

                # continually stack covariates based on column names
                past_covariate_whole = past_covariate_whole.stack(_temp_new_covariate)

        # Split the full scale covariate to train and val
        (
            past_covariate_train,
            past_covariate_val,
        ) = past_covariate_whole.split_before(train_split)
        return (
            past_covariate_whole,
            past_covariate_train,
            past_covariate_val,
        )
    else:
        return None, None, None


def early_stopper(patience: int, monitor: str = "train_loss"):
    my_stopper = EarlyStopping(
        monitor=monitor,
        patience=patience,
        min_delta=0,
        mode="min",
    )
    return my_stopper


def get_pl_kwargs(
    patience: int, monitor: str = "train_loss", accelerator: str = "cpu"
) -> Dict[str, Any]:
    my_stopper = early_stopper(5, "train_loss")
    pl_trainer_kwargs = {"callbacks": [my_stopper], "accelerator": "cpu"}
    return pl_trainer_kwargs


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
    probabilistic,
    export: str,
    low_quantile: float = None,
    high_quantile: float = None,
    forecast_only: bool = False,
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
    if forecast_only:
        ticker_series = ticker_series.drop_before(historical_fcast.start_time())
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

    if probabilistic:
        numeric_forecast = predicted_values.quantile_df()[f"{target_col}_0.5"].tail(
            n_predict
        )
    else:
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
    x = pd.to_datetime(x)
    x = x.strftime("%Y-%m-%d")
    return x


def get_series(data, target_col: str = None, is_scaler: bool = True):
    filler = MissingValuesFiller()
    filler_kwargs = dict(
        df=data,
        time_col="date",
        value_cols=[target_col],
        freq="B",
        fill_missing_dates=True,
    )
    try:
        ticker_series = TimeSeries.from_dataframe(**filler_kwargs)
    except ValueError:
        # remove business days to allow base lib to assume freq
        filler_kwargs.pop("freq")
        ticker_series = TimeSeries.from_dataframe(**filler_kwargs)

    if is_scaler:
        scaler = Scaler()
        scaled_ticker_series = scaler.fit_transform(
            filler.transform(ticker_series)
        ).astype(np.float32)
        return filler, scaler, scaled_ticker_series
    ticker_series = filler.transform(ticker_series).astype(np.float32)
    scaler = None
    return filler, scaler, ticker_series


def fit_model(
    model,
    series,
    val_series=None,
    past_covariates=None,
    val_past_covariates=None,
    **kwargs,
):
    fit_kwargs = dict(
        series=series,
    )
    fit_kwargs.update(kwargs)
    if val_series is not None:
        fit_kwargs["val_series"] = val_series
    if past_covariates is not None:
        fit_kwargs["past_covariates"] = past_covariates
        fit_kwargs["val_past_covariates"] = val_past_covariates

    model.fit(**fit_kwargs)


def get_prediction(
    model_name,
    probabilistic,
    use_scalers,
    scaler,
    past_covariates,
    best_model,
    ticker_series,
    past_covariate_whole,
    train_split,
    forecast_horizon,
    n_predict: int,
):
    # Historical backtest if with covariates
    if past_covariates is not None:
        historical_fcast = best_model.historical_forecasts(
            ticker_series,
            past_covariates=past_covariate_whole,
            start=train_split,
            forecast_horizon=forecast_horizon,
            retrain=False,
            verbose=True,
        )
    # historical backtest without covariates
    else:
        historical_fcast = best_model.historical_forecasts(
            ticker_series,
            start=train_split,
            forecast_horizon=forecast_horizon,
            retrain=False,
            verbose=True,
        )

    # now predict N days in the future
    if past_covariates is not None:
        if probabilistic:
            prediction = best_model.predict(
                series=ticker_series,
                past_covariates=past_covariate_whole,
                n=n_predict,
                num_samples=500,
            )
        else:
            prediction = best_model.predict(
                series=ticker_series,
                past_covariates=past_covariate_whole,
                n=n_predict,
            )
    else:
        if probabilistic:
            prediction = best_model.predict(
                series=ticker_series, n=n_predict, num_samples=500
            )
        else:
            prediction = best_model.predict(series=ticker_series, n=n_predict)

    precision = mape(
        actual_series=ticker_series, pred_series=historical_fcast
    )  # mape = mean average precision error
    console.print(f"{model_name} model obtains MAPE: {precision:.2f}% \n")

    # scale back
    if use_scalers:
        ticker_series = scaler.inverse_transform(ticker_series)
        historical_fcast = scaler.inverse_transform(historical_fcast)
        prediction = scaler.inverse_transform(prediction)

    return ticker_series, historical_fcast, prediction, precision, best_model


def check_parser_input(parser: argparse.ArgumentParser, datasets, *args) -> bool:
    # check proper file name is provided
    if not hasattr(parser, "target_dataset"):
        return False
    if not parser.target_dataset:  # type: ignore
        console.print("[red]Please enter valid dataset.\n[/red]")
        return False
    if "ignore_column" in args:
        return True
    if not hasattr(parser, "target_column"):
        return False

    # must check that target col is within target series
    if parser.target_column not in datasets[parser.target_dataset].columns:  # type: ignore
        console.print(
            f"[red]The column {parser.target_column} does not exist.\n[/red]"  # type: ignore
        )
        return False
    return True


def plot_residuals(
    model, past_covariates, series, forecast_horizon: int = 1, num_bins: int = 20
):
    if past_covariates:
        console.print(
            "[red]Cannot calculate and plot residuals if there are past covariates.[/red]"
        )
    else:
        console.print(
            "[green]Calculating and plotting residuals... This may take a few moments.[/green]"
        )
        my_stopper = early_stopper(5, "train_loss")
        pl_trainer_kwargs = {"callbacks": [my_stopper], "accelerator": "cpu"}
        model.pl_trainer_kwargs = pl_trainer_kwargs
        residuals = model.residuals(
            series=series, forecast_horizon=forecast_horizon, verbose=True
        )
        plot_residuals_analysis(residuals=residuals, num_bins=num_bins, fill_nan=True)

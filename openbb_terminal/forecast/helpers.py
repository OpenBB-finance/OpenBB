# pylint: disable=too-many-arguments
import os
import argparse
from typing import Any, Union, Optional, List, Dict, Tuple
from datetime import timedelta, datetime, time
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler, MaxAbsScaler, Normalizer
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    mean_squared_error,
)
from darts.dataprocessing.transformers import MissingValuesFiller, Scaler
from darts.utils.statistics import plot_residuals_analysis
from darts import TimeSeries
from darts.metrics import mape
from darts.models.forecasting.torch_forecasting_model import GlobalForecastingModel
from darts.explainability.shap_explainer import ShapExplainer
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from openbb_terminal.rich_config import console
from openbb_terminal.config_terminal import theme
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
    is_valid_axes_count,
)
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal import rich_config

logger = logging.getLogger(__name__)
logging.getLogger("pytorch_lightning").setLevel(logging.CRITICAL)  # No needed for now


def mean_absolute_percentage_error(y_true: np.ndarray, y_pred: np.ndarray) -> np.number:
    """Calculate mean absolute percent error"""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def print_prediction_kpis(real: np.ndarray, pred: np.ndarray):
    """Print prediction statistics"""
    kpis = {
        "MAPE": f"{mean_absolute_percentage_error(real, pred) :.3f} %",
        "R2": f"{r2_score(real, pred) :.3f}",
        "MAE": f"{mean_absolute_error(real, pred):.3f}",
        "MSE": f"{mean_squared_error(real, pred):.3f}",
        "RMSE": f"{mean_squared_error(real, pred, squared=False):.3f}",
    }
    df = pd.DataFrame.from_dict(kpis, orient="index")
    print_rich_table(
        df,
        show_index=True,
        title="KPIs",
        floatfmt=".2f",
    )


def plot_data_predictions(
    data,
    preds,
    y_valid,
    y_dates_valid,
    scaler,
    title,
    forecast_data,
    n_loops,
    time_str: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots data predictions for the different ML techniques
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    ax.plot(
        data.index,
        data.values,
        "-o",
        ms=2,
        label="Real data",
    )
    for i in range(len(y_valid) - 1):

        if scaler:
            y_pred = scaler.inverse_transform(preds[i].reshape(-1, 1)).ravel()
            y_act = scaler.inverse_transform(y_valid[i].reshape(-1, 1)).ravel()
        else:
            y_pred = preds[i].ravel()
            y_act = y_valid[i].ravel()
        ax.plot(
            y_dates_valid[i],
            y_pred,
            color=theme.down_color,
        )
        ax.fill_between(
            y_dates_valid[i],
            y_pred,
            y_act,
            where=(y_pred < y_act),
            color=theme.down_color,
            alpha=0.2,
        )
        ax.fill_between(
            y_dates_valid[i],
            y_pred,
            y_act,
            where=(y_pred > y_act),
            color=theme.up_color,
            alpha=0.2,
        )

    # Leave this out of the loop so that the legend doesn't get overpopulated with "Predictions"
    if scaler:
        final_pred = scaler.inverse_transform(preds[-1].reshape(-1, 1)).ravel()
        final_valid = scaler.inverse_transform(y_valid[-1].reshape(-1, 1)).ravel()
    else:
        final_pred = preds[-1].reshape(-1, 1).ravel()
        final_valid = y_valid[-1].reshape(-1, 1).ravel()
    ax.plot(
        y_dates_valid[-1],
        final_pred,
        color=theme.down_color,
        label="Predictions",
    )
    ax.fill_between(
        y_dates_valid[-1],
        final_pred,
        final_valid,
        alpha=0.2,
    )

    _, _, ymin, ymax = plt.axis()
    ax.vlines(
        forecast_data.index[0],
        ymin,
        ymax,
        linestyle="--",
    )
    if n_loops == 1:
        ax.plot(
            forecast_data.index,
            forecast_data.values,
            "-o",
            label="Forecast",
        )
    else:
        ax.plot(
            forecast_data.index,
            forecast_data.median(axis=1).values,
            "-o",
            label="Forecast",
        )
        ax.fill_between(
            forecast_data.index,
            forecast_data.quantile(0.25, axis=1).values,
            forecast_data.quantile(0.75, axis=1).values,
            alpha=0.3,
        )
    # Subtracting 1 day only for daily data.  For now if not daily, then start line on last point
    if (not time_str or time_str == "1D") and isinstance(
        forecast_data.index[0], datetime
    ):
        ax.axvspan(
            forecast_data.index[0] - timedelta(days=1),
            forecast_data.index[-1],
            alpha=0.2,
        )
        ax.set_xlim(data.index[0], forecast_data.index[-1] + timedelta(days=1))

    else:
        ax.axvspan(
            forecast_data.index[0],
            forecast_data.index[-1],
            alpha=0.2,
        )
        ax.set_xlim(data.index[0], forecast_data.index[-1])
    ax.set_title(title)
    ax.legend()
    ax.set_ylabel("Value")

    theme.style_primary_axis(ax)

    if external_axes is None:
        theme.visualize_output()


def prepare_scale_train_valid_test(
    data: Union[pd.DataFrame, pd.Series],
    n_input_days: int,
    n_predict_days: int,
    test_size: float,
    s_start_date: Optional[datetime] = None,
    s_end_date: Optional[datetime] = None,
    no_shuffle: bool = True,
    Preprocess: Optional[str] = "standardization",
):
    """
    Prepare and scale train, validate and test data. This is an old function for models
    imported from the previous pred menu

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe of stock prices
    ns_parser: argparse.Namespace
        Parsed arguments
    Returns
    -------
    X_train: np.ndarray
        Array of training data.  Shape (# samples, n_inputs, 1)
    X_test: np.ndarray
        Array of validation data.  Shape (total sequences - #samples, n_inputs, 1)
    y_train: np.ndarray
        Array of training outputs.  Shape (#samples, n_days)
    y_test: np.ndarray
        Array of validation outputs.  Shape (total sequences -#samples, n_days)
    X_dates_train: np.ndarray
        Array of dates for X_train
    X_dates_test: np.ndarray
        Array of dates for X_test
    y_dates_train: np.ndarray
        Array of dates for y_train
    y_dates_test: np.ndarray
        Array of dates for y_test
    test_data: np.ndarray
        Array of prices after the specified end date
    dates_test: np.ndarray
        Array of dates after specified end date
    scaler:
        Fitted PREPROCESSOR
    Preprocess: Optional[str]
        The method to preprocess data. Choose: standardization, minmax, normalization, or None.
        Default is standardization.
    """

    pre_dict = {
        "standardization": StandardScaler(),
        "minmax": MinMaxScaler(),
        "normalization": Normalizer(),
    }
    if Preprocess is None:
        scaler = None
    else:
        scaler = pre_dict.get(Preprocess, None)

    if s_end_date:
        data = data[data.index <= s_end_date]
        if n_input_days + n_predict_days > data.shape[0]:
            console.print(
                "Cannot train enough input days to predict with loaded dataframe\n"
            )
            return (
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                True,
            )
    if s_start_date:
        data = data[data.index >= s_start_date]
        if n_input_days + n_predict_days > data.shape[0]:
            console.print(
                "Cannot train enough input days to predict with loaded dataframe\n"
            )
            return (
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                True,
            )

    test_data = data.iloc[-n_input_days:]
    train_data = data.iloc[:-n_input_days]

    dates = data.index
    dates_test = test_data.index
    if scaler:
        train_data = scaler.fit_transform(data.values.reshape(-1, 1))
        test_data = scaler.transform(test_data.values.reshape(-1, 1))
    else:
        train_data = data.values.reshape(-1, 1)
        test_data = test_data.values.reshape(-1, 1)

    prices = train_data

    input_dates = []
    input_prices = []
    next_n_day_prices = []
    next_n_day_dates = []

    for idx in range(len(prices) - n_input_days - n_predict_days):
        input_prices.append(prices[idx : idx + n_input_days])  # noqa: E203
        input_dates.append(dates[idx : idx + n_input_days])  # noqa: E203
        next_n_day_prices.append(
            prices[
                idx + n_input_days : idx + n_input_days + n_predict_days  # noqa: E203
            ]
        )
        next_n_day_dates.append(
            dates[
                idx + n_input_days : idx + n_input_days + n_predict_days  # noqa: E203
            ]
        )

    input_dates = np.asarray(input_dates)  # type: ignore
    input_prices = np.array(input_prices)  # type: ignore
    next_n_day_prices = np.array(next_n_day_prices)  # type: ignore
    next_n_day_dates = np.asarray(next_n_day_dates)  # type: ignore

    (
        X_train,
        X_valid,
        y_train,
        y_valid,
        X_dates_train,
        X_dates_valid,
        y_dates_train,
        y_dates_valid,
    ) = train_test_split(
        input_prices,
        next_n_day_prices,
        input_dates,
        next_n_day_dates,
        test_size=test_size,
        shuffle=no_shuffle,
    )
    return (
        X_train,
        X_valid,
        y_train,
        y_valid,
        X_dates_train,
        X_dates_valid,
        y_dates_train,
        y_dates_valid,
        test_data,
        dates_test,
        scaler,
        False,
    )


def lambda_price_prediction_color(val: float) -> str:
    """Set prediction to be a colored string. This was changed to always shows blue"""
    return f"[#00AAFF]{val:.2f} [/#00AAFF]"


def print_pretty_prediction(df_pred: pd.DataFrame, last_price: float):
    """Print predictions"""
    if rich_config.USE_COLOR:
        df_pred = pd.DataFrame(df_pred)
        df_pred.columns = ["pred"]
        df_pred["pred"] = df_pred["pred"].apply(
            lambda x: lambda_price_prediction_color(x)
        )
    if check_dates(df_pred.index.to_series()):
        df_pred.index = df_pred.index.date
    print_rich_table(
        df_pred,
        show_index=True,
        index_name="Datetime",
        headers=["Prediction"],
        floatfmt=".2f",
        title=f"Actual price: [yellow]{last_price:.2f} [/yellow]",
    )


def past_covs(
    past_covariates: Optional[str],
    data: Union[pd.DataFrame, pd.Series],
    train_split: float,
    is_scaler: bool = True,
):
    if past_covariates is not None:

        target_covariates_names = past_covariates.split(",")

        # create first covariate to then stack
        console.print(f"[green]Covariate #0: {target_covariates_names[0]}[/green]")
        _, past_covariate_whole = get_series(
            data, target_column=target_covariates_names[0], is_scaler=is_scaler
        )

        if len(target_covariates_names) > 1:
            for i, column in enumerate(target_covariates_names[1:]):
                console.print(f"[green]Covariate #{i+1}: {column}[/green]")
                _, _temp_new_covariate = get_series(
                    data,
                    target_column=target_covariates_names[i + 1],
                    is_scaler=is_scaler,
                )

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
    return None, None, None


def early_stopper(patience: int, monitor: str = "val_loss"):
    my_stopper = EarlyStopping(
        monitor=monitor,
        patience=patience,
        min_delta=0.01,
        mode="min",
    )
    return my_stopper


def get_pl_kwargs(
    patience: int = 20, monitor: str = "val_loss", accelerator: str = "cpu"
) -> Dict[str, Any]:
    my_stopper = early_stopper(patience, monitor)
    pl_trainer_kwargs = {
        "callbacks": [my_stopper],
        "accelerator": accelerator,
        "logger": False,
        # "enable_progress_bar": False,
        "enable_model_summary": False,
    }
    return pl_trainer_kwargs


def plot_forecast(
    name: str,
    target_col: str,
    historical_fcast: type[TimeSeries],
    predicted_values: type[TimeSeries],
    ticker_series: type[TimeSeries],
    ticker_name: str,
    data: Union[pd.DataFrame, pd.Series],
    n_predict: int,
    forecast_horizon: int,
    past_covariates: Optional[str] = None,
    precision: Optional[int] = None,
    probabilistic: bool = False,
    export: str = "",
    low_quantile: float = None,
    high_quantile: float = None,
    forecast_only: bool = False,
    naive: bool = False,
    export_pred_raw: bool = False,
    external_axes: Optional[List[plt.axes]] = None,
):
    quant_kwargs = {}
    if low_quantile:
        quant_kwargs["low_quantile"] = low_quantile
    if high_quantile:
        quant_kwargs["high_quantile"] = high_quantile
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        ax = external_axes[0]

    # ax = fig.get_axes()[0] # fig gives list of axes (only one for this case)
    naive_fcast: type[TimeSeries] = ticker_series.shift(1)
    if forecast_only:
        ticker_series = ticker_series.drop_before(historical_fcast.start_time())
    ticker_series.plot(label=target_col, ax=ax)
    historical_fcast.plot(
        label=f"Backtest {forecast_horizon}-Steps ahead forecast",
        ax=ax,
        **quant_kwargs,
    )

    if naive:
        # show naive forecast shift timeseries by 1
        naive_fcast = naive_fcast.drop_before(historical_fcast.start_time())
        naive_precision = mape(ticker_series, naive_fcast)

        naive_fcast.plot(
            label=f"Naive+1: {naive_precision:.2f}%",
            ax=ax,
            **quant_kwargs,
        )

    pred_label = f"{name} Forecast"
    if past_covariates:
        pred_label += " w/ past covs"
    predicted_values.plot(label=pred_label, **quant_kwargs, color="#00AAFF")
    ax.set_title(
        f"{name} for <{ticker_name}> for next [{n_predict}] days (MAPE={precision:.2f}%)"
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

    # user wants to export plot
    export_data(export, os.path.dirname(os.path.abspath(__file__)), name)

    # user wants to export only raw predictions
    if export_pred_raw:
        # convert numeric)forecast to dataframe
        numeric_forecast = numeric_forecast.to_frame()

        # if numeric_forcast has a column with *_0.5, then rename it to target_col
        if f"{target_col}_0.5" in numeric_forecast.columns:
            numeric_forecast.rename(
                columns={f"{target_col}_0.5": target_col}, inplace=True
            )

        # convert non-date column to 2 decimal places
        numeric_forecast[target_col] = numeric_forecast[target_col].apply(
            lambda x: round(x, 2)
        )

        export_data(
            "csv",
            os.path.dirname(os.path.abspath(__file__)),
            name + "_predictions",
            numeric_forecast,
        )


def plot_explainability(
    model: type[GlobalForecastingModel],
    explainability_raw=False,
    external_axes: Optional[List[plt.axes]] = None,
):
    """
    Plot explainability of the model

    Parameters
    ----------
    model: type[GlobalForecastingModel]
        The model to plot explainability for
    explainability_raw: bool
        Whether to plot raw explainability or not
        external_axes: Optional[List[plt.axes]]
        Optional list of axes to plot on

    Returns
    -------
    None
    """
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        ax = external_axes[0]

    shap_explain = ShapExplainer(model)
    shap_explain.summary_plot(horizons=1)
    if explainability_raw:
        console.print("\n")
        console.print("[green]Exporting Raw Explainability DataFrame[/green]")
        raw_df = shap_explain.explain().get_explanation(horizon=1).pd_dataframe()
        export_data(
            "csv",
            os.path.dirname(os.path.abspath(__file__)),
            "explainability_raw",
            raw_df,
        )

    ax.yaxis.set_label_position("left")
    ax.yaxis.tick_left()

    # change the colour of the y axis tick labels
    for t in ax.get_yticklabels():
        t.set_color("white")

    # change the colour of the x axis tick labels
    for t in ax.get_xticklabels():
        t.set_color("white")

    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()


def dt_format(x) -> str:
    """Convert any Timestamp to YYYY-MM-DD
    Args:
        x: Pandas Timestamp of any length
    Returns:
        x: formatted string
    """
    x = pd.to_datetime(x)
    x = x.strftime("%Y-%m-%d")
    return x


def get_series(
    data: pd.DataFrame,
    target_column: str = None,
    is_scaler: bool = True,
    time_col: str = "date",
) -> Tuple[Optional[Scaler], TimeSeries]:
    filler = MissingValuesFiller()
    filler_kwargs = dict(
        df=data,
        time_col=time_col,
        value_cols=[target_column],
        freq="B",
        fill_missing_dates=True,
    )
    try:
        # for the sdk, we must check if date is a column not an index
        # check if date is in the index, if true, reset the index
        if time_col in data.index.names:
            # # make a new column with the index
            data[time_col] = data.index
            # reset the index
            data.reset_index(drop=True, inplace=True)
            # remove 00:00:00 from 2019-11-19 00:00:00
            data[time_col] = data[time_col].apply(lambda x: dt_format(x))

        ticker_series = TimeSeries.from_dataframe(**filler_kwargs)
    except ValueError:
        # remove business days to allow base lib to assume freq
        filler_kwargs.pop("freq")
        ticker_series = TimeSeries.from_dataframe(**filler_kwargs)
    except AttributeError:
        # Uses index if no date column
        console.print(
            "[red]Warning: no date found, assuming items evenly spaced.[/red]\n"
        )
        filler_kwargs.pop("time_col")
        ticker_series = TimeSeries.from_dataframe(**filler_kwargs)

    if is_scaler:
        scaler = Scaler(scaler=MaxAbsScaler())
        scaled_ticker_series = scaler.fit_transform(
            filler.transform(ticker_series)
        ).astype(np.float32)
        return scaler, scaled_ticker_series
    ticker_series = filler.transform(ticker_series).astype(np.float32)
    scaler = None
    return scaler, ticker_series


def fit_model(
    model: type[GlobalForecastingModel],
    series: TimeSeries,
    val_series: Optional[TimeSeries] = None,
    past_covariates: Optional[TimeSeries] = None,
    val_past_covariates: Optional[TimeSeries] = None,
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
    model_name: str,
    probabilistic: bool,
    use_scalers: bool,
    scaler: Optional[Scaler],
    past_covariates: Optional[str],
    best_model: type[GlobalForecastingModel],
    ticker_series: TimeSeries,
    past_covariate_whole: Optional[TimeSeries],
    train_split: float,
    forecast_horizon: int,
    n_predict: int,
):
    _, val = ticker_series.split_before(train_split)

    print(f"Predicting {model_name} for {n_predict} days")
    if model_name not in ["Regression", "Logistic Regression"]:
        # need to create a new pytorch trainer for historical backtesting to remove progress bar
        best_model.trainer = None
        best_model.trainer_params["enable_progress_bar"] = False

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
        actual_series=val, pred_series=historical_fcast
    )  # mape = mean average percentage error
    console.print(f"{model_name} model obtains MAPE: {precision:.2f}% \n")

    # scale back
    if use_scalers and isinstance(scaler, Scaler):
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

    # must check that data["date"] col is within target series
    if parser.target_column not in datasets[parser.target_dataset].columns:  # type: ignore
        console.print(
            f"[red]The column {parser.target_column} does not exist.\n[/red]"  # type: ignore
        )
        return False
    return True


def plot_residuals(
    model: type[GlobalForecastingModel],
    past_covariates: Optional[str],
    series: Optional[Union[type[TimeSeries], List[type[TimeSeries]], List[np.ndarray]]],
    forecast_horizon: int = 1,
    num_bins: int = 20,
    default_formatting: bool = False,
):
    if past_covariates:
        console.print(
            "[red]Cannot calculate and plot residuals if there are past covariates.[/red]"
        )
    else:
        console.print(
            "[green]Calculating and plotting residuals... This may take a few moments.[/green]"
        )
        my_stopper = early_stopper(5, "val_loss")
        pl_trainer_kwargs = {"callbacks": [my_stopper], "accelerator": "cpu"}
        model.trainer_params = pl_trainer_kwargs
        residuals = model.residuals(
            series=series,
            forecast_horizon=forecast_horizon,
            retrain=False,
            verbose=True,
        )
        plot_residuals_analysis(
            residuals=residuals,
            num_bins=num_bins,
            fill_nan=True,
            default_formatting=default_formatting,
        )


def check_data_length(
    train, test, input_chunk_length: int, output_chunk_length: int
) -> bool:
    if input_chunk_length + output_chunk_length > len(train):
        base = "[red]Not enough train data. Please increase the "
        console.print(
            base + "train test split or decrease input or output chunk length.[/red]\n"
        )
        return False
    if input_chunk_length + output_chunk_length > len(test):
        base = "[red]Not enough test data. Please decrease the "
        console.print(
            base
            + "train test split or decrease the input or output chunk length.[/red]\n"
        )
        return False
    return True


def filter_dates(
    data: Union[pd.DataFrame, pd.Series],
    start_date: Optional[datetime],
    end_date: Optional[datetime],
) -> Union[pd.DataFrame, pd.Series]:
    if start_date and end_date and start_date >= end_date:
        console.print("[red]The start date must be before the end date.[/red]\n")
        return data
    if end_date:
        data = data[data["date"] <= end_date]
    if start_date:
        data = data[data["date"] >= start_date]
    return data


def clean_data(
    data: Union[pd.DataFrame, pd.Series],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    target_column: Optional[str] = None,
    past_covariates: Optional[str] = None,
) -> Union[pd.DataFrame, pd.Series]:
    # check if target column is in data and if the target_column has any inf
    # replace all inf with nan. This is because darts does not handle inf
    # Creating a timeseries with fillna=True will replace all nan with interoplated values
    if target_column and target_column in data.columns:
        if data[target_column].isin([np.inf, -np.inf]).any():
            console.print(
                f"[red]The target column [{target_column}] has inf values. Cleaning...[/red]\n"
            )
            data = data.replace([np.inf, -np.inf], np.nan)

    # check if past covariates are in data and if they have any inf
    if past_covariates:
        covariates = past_covariates.split(",")
        for covariate in covariates:
            if covariate in data.columns:
                if data[covariate].isin([np.inf, -np.inf]).any():
                    console.print(
                        f"[red]The covariate:{covariate} has inf values. Cleaning...[/red]\n"
                    )
                    data = data.replace([np.inf, -np.inf], np.nan)

    if isinstance(data, pd.Series):
        col = data.name
        columns = ["date", col]
        data = pd.DataFrame(data).reset_index()
        data.columns = columns
        data = filter_dates(data, start_date, end_date)
        data = data.set_index("date")
        data = data[col]
    elif "date" in data.columns:
        data = filter_dates(data, start_date, end_date)
    elif end_date or start_date:
        console.print(
            "[red]No 'date' column specified, ignoring start end end date[/red]\n"
        )
    return data


def clean_covariates(parser, dataset: pd.DataFrame) -> Optional[str]:
    forecast_column: str = parser.target_column
    if parser.all_past_covariates:
        data = dataset
        covs = [x for x in data.columns if x not in ["date", parser.target_column]]
        return ",".join(covs)
    covariates = parser.past_covariates
    if not covariates:
        return covariates
    covs_list = covariates.split(",")
    for covariate in covs_list:
        if covariate == forecast_column:
            covs_list.remove(covariate)
            console.print(
                f"[red]Forecast target '{forecast_column}' cannot be within the past"
                " covariates. Removed the covariates from analysis[/red]\n"
            )
    if len(covariates) == 0:
        return None
    covariates = ",".join(covs_list)
    return covariates


def check_data(
    data: pd.DataFrame, target_column: str, past_covariates: Optional[str] = None
) -> bool:
    if target_column not in data.columns:
        console.print(
            f"[red]Column {target_column} is not in the dataframe."
            " Change the 'target_column' parameter.[/red]\n"
        )
        return False
    if past_covariates is not None:
        covariates = past_covariates.split(",")
        for covariate in covariates:
            if covariate not in data.columns:
                console.print(
                    f"[red]Column {covariate} is not in the dataframe."
                    " Change the 'past_covariates' parameter.[/red]\n"
                )
                return False
    return True


def check_output(
    output_chunk_length: int, n_predict: int, past_covariates: bool
) -> int:
    if past_covariates:
        if output_chunk_length != n_predict:
            console.print(
                "[red]Warning: when using past covariates n_predict must equal"
                f" output_chunk_length. We have changed your output_chunk_length to {n_predict}"
                " to match your n_predict"
            )
        return n_predict
    return output_chunk_length


def check_dates(s: pd.Series) -> bool:
    """Checks whether all hours, minutes, seconds and milliseconds are 0""" ""
    for _, value in s.items():
        try:
            if value.time() != time(0, 0, 0, 0):
                return False
        except AttributeError:
            return False
    return True

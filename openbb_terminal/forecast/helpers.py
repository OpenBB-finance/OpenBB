# pylint: disable=too-many-arguments,too-many-lines
import argparse
import logging
import os
from datetime import datetime, time, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from darts import TimeSeries
from darts.dataprocessing.transformers import MissingValuesFiller, Scaler
from darts.explainability.shap_explainer import ShapExplainer
from darts.metrics import mape, mse, rmse, smape
from darts.models.forecasting.torch_forecasting_model import GlobalForecastingModel
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from shap import Explanation
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MaxAbsScaler, MinMaxScaler, Normalizer, StandardScaler

from openbb_terminal import OpenBBFigure, rich_config, theme
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

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
    external_axes: bool = False,
):
    """Plots data predictions for the different ML techniques
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    fig = OpenBBFigure()
    fig.add_scatter(
        x=data.index,
        y=data.values,
        mode="lines+markers",
        line=dict(color=theme.up_color),
        name="Real data",
    )
    for i in range(len(y_valid) - 1):
        if scaler:
            y_pred = scaler.inverse_transform(preds[i].reshape(-1, 1)).ravel()
            y_act = scaler.inverse_transform(y_valid[i].reshape(-1, 1)).ravel()
        else:
            y_pred = preds[i].ravel()
            y_act = y_valid[i].ravel()

        fig.add_scatter(
            x=y_dates_valid[i],
            y=y_pred,
            mode="lines",
            line=dict(color=theme.down_color),
            name="Predictions",
        )
        fig.add_scatter(
            x=y_dates_valid[i],
            y=y_act,
            mode="lines",
            line=dict(color=theme.up_color),
            name="Actual",
        )

    # Leave this out of the loop so that the legend doesn't get overpopulated with "Predictions"
    if scaler:
        final_pred = scaler.inverse_transform(preds[-1].reshape(-1, 1)).ravel()
        final_valid = scaler.inverse_transform(y_valid[-1].reshape(-1, 1)).ravel()
    else:
        final_pred = preds[-1].reshape(-1, 1).ravel()
        final_valid = y_valid[-1].reshape(-1, 1).ravel()

    fig.add_scatter(
        x=y_dates_valid[-1],
        y=final_pred,
        mode="lines",
        line=dict(color=theme.down_color),
        name="Predictions",
    )
    fig.add_scatter(
        x=y_dates_valid[-1],
        y=final_valid,
        mode="lines",
        line=dict(color=theme.up_color),
        name="Actual",
    )

    fig.add_vline(
        x=forecast_data.index[0], line=dict(width=1, dash="dash", color="white")
    )
    if n_loops == 1:
        fig.add_scatter(
            x=forecast_data.index,
            y=forecast_data.values,
            mode="lines",
            line=dict(color=theme.up_color),
            name="Forecast",
        )

    else:
        fig.add_scatter(
            x=forecast_data.index,
            y=forecast_data.median(axis=1).values,
            mode="lines",
            line=dict(color=theme.up_color),
            name="Forecast",
        )
        fig.add_scatter(
            x=forecast_data.index,
            y=forecast_data.quantile(0.25, axis=1).values,
            mode="lines",
            line=dict(color=theme.up_color),
            name="Forecast",
        )

    ymin, ymax = fig.layout.yaxis.range
    # Subtracting 1 day only for daily data.  For now if not daily, then start line on last point
    if (not time_str or time_str == "1D") and isinstance(
        forecast_data.index[0], datetime
    ):
        fig.add_shape(
            type="rect",
            x0=forecast_data.index[0] - timedelta(days=1),
            y0=ymin,
            x1=forecast_data.index[-1],
            y1=ymax,
            fillcolor=theme.up_color,
            opacity=0.2,
            layer="below",
            line_width=0,
        )
        fig.update_xaxes(
            range=[data.index[0], forecast_data.index[-1] + timedelta(days=1)]
        )

    else:
        fig.add_shape(
            type="rect",
            x0=forecast_data.index[0],
            y0=ymin,
            x1=forecast_data.index[-1],
            y1=ymax,
            fillcolor=theme.up_color,
            opacity=0.2,
            layer="below",
            line_width=0,
        )
        fig.update_xaxes(range=[data.index[0], forecast_data.index[-1]])

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Price",
    )
    return fig.show(external=external_axes)


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
    scaler = None if Preprocess is None else pre_dict.get(Preprocess, None)

    if s_end_date:
        data = data[data.index <= s_end_date]
        if n_input_days + n_predict_days > data.shape[0]:
            console.print(
                "Cannot train enough input days to predict with loaded dataframe\n"
            )
            return (None * 11, True)  # type: ignore
    if s_start_date:
        data = data[data.index >= s_start_date]
        if n_input_days + n_predict_days > data.shape[0]:
            console.print(
                "Cannot train enough input days to predict with loaded dataframe\n"
            )
            return (None * 11, True)  # type: ignore

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


def print_pretty_prediction(df_pred: pd.DataFrame, last_price: float):
    """Print predictions"""

    if rich_config.USE_COLOR:
        df_pred = pd.DataFrame(df_pred)
        df_pred.columns = ["pred"]
        if not get_current_user().preferences.USE_INTERACTIVE_DF:
            df_pred["pred"] = df_pred["pred"].apply(
                lambda x: f"[#00AAFF]{x:.2f} [/#00AAFF]"
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
        # "logger": False,
        # "enable_progress_bar": False,
        "enable_model_summary": False,
    }
    return pl_trainer_kwargs


@log_start_end(log=logger)
def plot_predicted(
    predicted_values: type[TimeSeries],
    fig: OpenBBFigure,
    central_quantile: Union[float, str] = 0.5,
    low_quantile: Optional[float] = 0.05,
    high_quantile: Optional[float] = 0.95,
    label: Optional[Union[str, List[str]]] = "",
):
    """Plots the predicted_values time series on the given figure.

    Parameters
    ----------
    predicted_values: TimeSeries
        The predicted values TimeSeries.
    fig: OpenBBFigure
        The figure to plot on.
    central_quantile: float or str
        The quantile (between 0 and 1) to plot as a "central" value, if the series is stochastic (i.e., if
        it has multiple samples). This will be applied on each component separately (i.e., to display quantiles
        of the components' marginal distributions). For instance, setting `central_quantile=0.5` will plot the
        median of each component. `central_quantile` can also be set to 'mean'.
    low_quantile: float
        The quantile to use for the lower bound of the plotted confidence interval. Similar to `central_quantile`,
        this is applied to each component separately (i.e., displaying marginal distributions). No confidence
        interval is shown if `confidence_low_quantile` is None (default 0.05).
    high_quantile: float
        The quantile to use for the upper bound of the plotted confidence interval. Similar to `central_quantile`,
        this is applied to each component separately (i.e., displaying marginal distributions). No confidence
        interval is shown if `high_quantile` is None (default 0.95).
    label: str or list of str
        A prefix that will appear in front of each component of the TimeSeries or a list of string of
        length the number of components in the plotted TimeSeries (default "").
    """

    if central_quantile != "mean" and not (
        isinstance(central_quantile, float) and 0.0 <= central_quantile <= 1.0
    ):
        raise ValueError(
            'central_quantile must be either "mean", or a float between 0 and 1.'
        )

    if (
        high_quantile is not None
        and low_quantile is not None
        and not (0.0 <= low_quantile <= 1.0 and 0.0 <= high_quantile <= 1.0)
    ):
        raise ValueError(
            "confidence interval low and high quantiles must be between 0 and 1."
        )

    if predicted_values.n_components > 10:
        logger.warning(
            "Number of components is larger than 10 (%s). Plotting only the first 10 components.",
            predicted_values.n_components,
        )

    if not isinstance(label, str) and isinstance(label, list):
        if not (
            len(label) == predicted_values.n_components
            or (predicted_values.n_components > 10 and len(label) >= 10)
        ):
            console.print(
                "The label argument should have the same length as the number of plotted components "
                f"({min(predicted_values.n_components, 10)}), only {len(label)} labels were provided"
            )
    else:
        pass

    # pylint: disable=protected-access
    for i, c in enumerate(predicted_values._xa.component[:10]):
        comp_name = str(c.values)
        comp = predicted_values._xa.sel(component=c)

        if comp.sample.size > 1:
            if central_quantile == "mean":
                central_series = comp.mean(dim="sample")
            else:
                central_series = comp.quantile(q=central_quantile, dim="sample")
        else:
            central_series = comp.mean(dim="sample")

        if isinstance(label, list):
            label_to_use = label[i]
        else:
            label_to_use = (
                (f"{label}" + (f"_{i}" if len(predicted_values.components) > 1 else ""))
                if label != ""
                else comp_name
            )

        if central_series.shape[0] > 1:
            for col in central_series.coords:
                if isinstance(central_series.coords[col].values[0], np.datetime64):
                    central_series = central_series.rename({col: "date"})
                    break

            fig.add_scatter(
                x=central_series.date,
                y=central_series.values,
                mode="lines",
                name=label_to_use,
                line=dict(width=2, color=theme.up_color),
            )

        elif central_series.shape[0] == 1:
            fig.add_scatter(
                x=[predicted_values.start_time()],
                y=[central_series.values[0]],
                mode="markers",
                name=label_to_use,
            )

        # Optionally show confidence intervals
        if (
            comp.sample.size > 1
            and low_quantile is not None
            and high_quantile is not None
        ):
            low_series = comp.quantile(q=low_quantile, dim="sample")
            high_series = comp.quantile(q=high_quantile, dim="sample")
            if low_series.shape[0] > 1:
                # plotly fill
                fig.add_scatter(
                    x=predicted_values.time_index,
                    y=high_series,
                    name=f"High Confidence Interval ({high_quantile * 100}%)",
                    mode="lines",
                    line_width=0,
                    opacity=0.2,
                    showlegend=False,
                )
                fig.add_scatter(
                    x=predicted_values.time_index,
                    y=low_series,
                    name=f"Low Confidence Interval ({low_quantile * 100}%)",
                    fill="tonexty",
                    mode="lines",
                    fillcolor=theme.up_color_transparent.replace("0.50", "0.35"),
                    line_width=0,
                    opacity=0.2,
                    showlegend=False,
                )

            else:
                fig.add_scatter(
                    x=[predicted_values.start_time(), predicted_values.start_time()],
                    y=[low_series.values[0], high_series.values[0]],
                    mode="lines",
                    name=label_to_use,
                    line_color=theme.up_color,
                )

    return fig


@log_start_end(log=logger)
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
    sheet_name: Optional[str] = None,
    low_quantile: Optional[float] = None,
    high_quantile: Optional[float] = None,
    forecast_only: bool = False,
    naive: bool = False,
    export_pred_raw: bool = False,
    metric: str = "mape",
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    quant_kwargs = {}
    if low_quantile:
        quant_kwargs["low_quantile"] = low_quantile
    if high_quantile:
        quant_kwargs["high_quantile"] = high_quantile

    naive_fcast: type[TimeSeries] = ticker_series.shift(1)
    if forecast_only:
        ticker_series = ticker_series.drop_before(historical_fcast.start_time())

    fig = OpenBBFigure(yaxis_title=target_col, xaxis_title="Date")
    fig.set_title(
        f"{name} for <{ticker_name}> for next [{n_predict}]"
        f" days ({metric.upper()}={precision:.2f}%)"
    )

    fig.add_scatter(
        y=list(ticker_series.univariate_values()),
        x=list(ticker_series.time_index),
        name="Actual",
        line_color="gold",
        mode="lines",
    )

    fig.add_scatter(
        y=list(historical_fcast.univariate_values()),
        x=list(historical_fcast.time_index),
        name=f"Backtest {forecast_horizon}-Steps ahead forecast",
        line_color="red",
        mode="lines",
    )

    if naive:
        # show naive forecast shift timeseries by 1
        naive_fcast = naive_fcast.drop_before(historical_fcast.start_time())

        # calculate precision based on metric
        if metric == "rsme":
            naive_precision = rmse(ticker_series, naive_fcast)
        elif metric == "mse":
            naive_precision = mse(ticker_series, naive_fcast)
        elif metric == "mape":
            naive_precision = mape(ticker_series, naive_fcast)
        elif metric == "smape":
            naive_precision = smape(ticker_series, naive_fcast)

        fig.add_scatter(
            y=list(naive_fcast.univariate_values()),
            x=list(naive_fcast.time_index),
            name=f"Naive+1: {naive_precision:.2f}%",
            line_color="green",
            mode="lines",
        )

    pred_label = f"{name} Forecast"
    if past_covariates:
        pred_label += " w/ past covs"

    fig = plot_predicted(predicted_values, fig, label=pred_label, **quant_kwargs)

    fig.update_layout(title=dict(x=0.5, xanchor="center", yanchor="top"))
    fig.update_xaxes(
        range=[
            ticker_series.start_time(),
            ticker_series.end_time() + timedelta(days=30 + n_predict),
        ],
        autorange=False,
    )

    if probabilistic:
        numeric_forecast = predicted_values.quantile_df()[f"{target_col}_0.5"].tail(
            n_predict
        )
    else:
        numeric_forecast = predicted_values.pd_dataframe()[target_col].tail(n_predict)

    print_pretty_prediction(numeric_forecast, data[target_col].iloc[-1])

    # user wants to export plot
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        name,
        sheet_name=sheet_name,
        figure=fig,
    )

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
            sheet_name,
        )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def plotly_shap_scatter_plot(
    shap_values: Explanation,
    features: Optional[Union[pd.DataFrame, list, np.ndarray]] = None,
    feature_names: Optional[Union[List[str], np.ndarray]] = None,
    max_display: Optional[int] = None,
) -> OpenBBFigure:
    """Generate a shap values summary plot where features are ranked from
    highest mean absolute shap value to lowest, with point clouds shown
    for each feature.

    Parameters:
    -----------
    shap_exp: Explanation
        The shap values for the model.
    features : Optional[Union[pd.DataFrame, list, np.ndarray]]
        Matrix of feature values (# samples x # features) or a feature_names list as shorthand
    feature_names : Optional[List[str]]
        Names of the features (length # features)
    max_display: Optional[int]
        The maximum number of features to display. Defaults to 20.

    Returns:
    --------
    OpenBBFigure
        The shap values summary plot.
    """
    if max_display is None:
        max_display = 20

    shap_exp = shap_values
    shap_values = shap_exp.values
    if features is None:
        features = shap_exp.data
    if feature_names is None:
        feature_names = shap_exp.feature_names

    idx2cat = None
    # convert from a DataFrame or other types
    if isinstance(features, pd.DataFrame):
        if feature_names is None:
            feature_names = features.columns
        # feature index to category flag
        idx2cat = features.dtypes.astype(str).isin(["object", "category"]).tolist()
        features = features.values
    elif isinstance(features, list):
        if feature_names is None:
            feature_names = features
        features = None
    elif (features is not None) and len(features.shape) == 1 and feature_names is None:
        feature_names = features
        features = None

    num_features = shap_values.shape[1]

    if feature_names is None:
        feature_names = np.array([f"Feature {i}" for i in range(num_features)])

    feature_order = np.argsort(np.sum(np.abs(shap_values), axis=0))
    feature_order = feature_order[-min(max_display, len(feature_order)) :]

    fig = OpenBBFigure.create_subplots(
        1, 2, specs=[[{}, {}]], column_widths=[0.01, 0.99], horizontal_spacing=0
    )
    fig.set_xaxis_title("SHAP value (impact on model output)")

    for pos, i in enumerate(feature_order):
        pos += 2
        shaps = shap_values[:, i]
        values = None if features is None else features[:, i]
        inds = np.arange(len(shaps))
        np.random.shuffle(inds)
        if values is not None:
            values = values[inds]
        shaps = shaps[inds]

        colored_feature = True
        try:
            if idx2cat is not None and idx2cat[i]:  # check categorical feature
                colored_feature = False
            else:
                values = np.array(
                    values, dtype=np.float64
                )  # make sure this can be numeric
        except Exception:
            colored_feature = False

        N = len(shaps)
        nbins = 100
        quant = np.round(
            nbins * (shaps - np.min(shaps)) / (np.max(shaps) - np.min(shaps) + 1e-8)
        )
        inds = np.argsort(quant + np.random.randn(N) * 1e-6)
        layer = 0
        last_bin = -1

        ys = np.zeros(N)
        for ind in inds:
            if quant[ind] != last_bin:
                layer = 0
            ys[ind] = np.ceil(layer / 2) * ((layer % 2) * 2 - 1)
            layer += 1
            last_bin = quant[ind]
        ys *= 0.9 * (0.4 / np.max(ys + 1))

        if features is not None and colored_feature:
            # trim the color range, but prevent the color range from collapsing
            vmin = np.nanpercentile(values, 5)
            vmax = np.nanpercentile(values, 95)
            if vmin == vmax:
                vmin = np.nanpercentile(values, 1)
                vmax = np.nanpercentile(values, 99)
                if vmin == vmax:
                    vmin = np.min(values)
                    vmax = np.max(values)

            # fixes rare numerical precision issues
            vmin = min(vmin, vmax)

            # plot the nan values in the interaction feature as grey
            nan_mask = np.isnan(values)
            fig.add_scattergl(
                x=shaps[nan_mask],
                y=pos + ys[nan_mask],
                mode="markers",
                marker=dict(
                    color="#777777",
                    cmin=vmin,
                    cmax=vmax,
                    size=10,
                ),
                hoverinfo="none",
                showlegend=False,
                row=1,
                col=2,
            )
            # plot the non-nan values colored by the trimmed feature value
            cvals = values[np.invert(nan_mask)].astype(np.float64)
            cvals_imp = cvals.copy()
            cvals_imp[np.isnan(cvals)] = (vmin + vmax) / 2.0
            cvals[cvals_imp > vmax] = vmax
            cvals[cvals_imp < vmin] = vmin

            fig.add_scattergl(
                x=shaps[np.invert(nan_mask)],
                y=pos + ys[np.invert(nan_mask)],
                mode="markers",
                marker=dict(
                    color=cvals,
                    colorscale="Bluered",
                    showscale=bool(pos == 2),
                    colorbar=dict(
                        x=-0.05,
                        thickness=10,
                        xpad=0,
                        thicknessmode="pixels",
                        title=dict(
                            text="Feature Value",
                            side="right",
                            font=dict(size=12),
                        ),
                        tickmode="array",
                        tickvals=[vmin, vmax],
                        ticktext=["Low", "High"],
                        tickfont=dict(size=12),
                        ticklabelposition="outside left",
                        borderwidth=0,
                    ),
                    cmin=vmin,
                    cmax=vmax,
                    size=10,
                ),
                hoverinfo="none",
                name=feature_names[i],
                showlegend=False,
                row=1,
                col=2,
            )

    display_columns = [feature_names[i] for i in feature_order]
    fig.update_yaxes(
        position=0,
        tickmode="array",
        ticktext=display_columns,
        tickvals=np.arange(2, len(display_columns) + 2),
        automargin=False,
        range=[1.5, len(display_columns) + 1.5],
    )
    fig.update_layout(
        margin=dict(r=190, l=20),
        height=100 + len(display_columns) * 50,
    )

    return fig


@log_start_end(log=logger)
def plot_explainability(
    model: type[GlobalForecastingModel],
    explainability_raw: bool = False,
    sheet_name: Optional[str] = None,
    export: str = "",
    external_axes: bool = False,
) -> Union[None, OpenBBFigure]:
    """
    Plot explainability of the model

    Parameters
    ----------
    model: type[GlobalForecastingModel]
        The model to plot explainability for
    explainability_raw: bool
        Whether to plot raw explainability or not
    sheet_name: Optional[str]
        Optionally specify the name of the sheet the data is exported to.
    export: (str, optional)
        Export data to csv, jpg, png, or pdf. Defaults to "".
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """

    shap_explain = ShapExplainer(model)

    # pylint: disable=W0212
    horizons, target_components = shap_explain._check_horizons_and_targets(1, None)

    foreground_X_sampled = shap_explain.explainers.background_X

    shaps_ = shap_explain.explainers.shap_explanations(
        foreground_X_sampled, horizons, target_components
    )
    for t in target_components:
        for h in horizons:
            fig = plotly_shap_scatter_plot(shaps_[h][t], foreground_X_sampled)
            fig.set_title(f"Target: `{t}` - Horizon: t+{h}")
            fig.add_vline(x=0, line_width=1.5, line_color="white", opacity=0.7)

    if explainability_raw:
        console.print("\n")
        console.print("[green]Exporting Raw Explainability DataFrame[/green]")
        raw_df = shap_explain.explain().get_explanation(horizon=1).pd_dataframe()
        export_data(
            "csv",
            os.path.dirname(os.path.abspath(__file__)),
            "explainability_raw",
            raw_df,
            sheet_name,
        )

    fig.cmd_xshift = -20
    if fig.is_image_export(export):
        name, ext = export.split(".") if "." in export else (None, None)
        if name and ext:
            export = f"{name}_explainability.{ext}"
        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "explainability",
            figure=fig,
        )

    return fig.show(external=external_axes)


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
    target_column: Optional[str] = None,
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


@log_start_end(log=logger)
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
    metric: str,
):
    _, val = ticker_series.split_before(train_split)

    print(f"Predicting {model_name} for {n_predict} days")
    if model_name not in ["Regression", "Logistic Regression"]:
        # need to create a new pytorch trainer for historical backtesting to remove progress bar
        best_model.trainer = None
        # best_model.trainer_params["enable_progress_bar"] = True

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

    # calculate precision based on metric (rmse, mse, mape)
    if metric == "rmse":
        precision = rmse(actual_series=val, pred_series=historical_fcast)
    elif metric == "mse":
        precision = mse(actual_series=val, pred_series=historical_fcast)
    elif metric == "mape":
        precision = mape(actual_series=val, pred_series=historical_fcast)
    elif metric == "smape":
        precision = smape(actual_series=val, pred_series=historical_fcast)

    console.print(f"{model_name} model obtains {metric.upper()}: {precision:.2f}% \n")

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


@log_start_end(log=logger)
def plot_residuals(
    model: type[GlobalForecastingModel],
    past_covariates: Optional[str],
    series: Optional[Union[type[TimeSeries], List[type[TimeSeries]], List[np.ndarray]]],
    forecast_horizon: int = 1,
    num_bins: int = 20,
    default_formatting: bool = False,
):
    del default_formatting

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
        residuals: TimeSeries = model.residuals(
            series=series,
            forecast_horizon=forecast_horizon,
            retrain=False,
            verbose=True,
        )

        residuals._assert_univariate()  # pylint: disable=protected-access

        fig = OpenBBFigure.create_subplots(
            rows=2,
            cols=2,
            shared_xaxes=False,
            subplot_titles=("Residuals Values", "ACF", "Distribution"),
            specs=[
                [{"colspan": 2}, None],  # type: ignore
                [{"type": "scatter"}, {"type": "histogram"}],
            ],
        )
        fig.set_xaxis_title("date", row=1, col=1)
        fig.set_yaxis_title("value", row=1, col=1)
        fig.set_xaxis_title("lag", row=2, col=1)
        fig.set_yaxis_title("ACF value", row=2, col=1)
        fig.set_xaxis_title("value", row=2, col=2)
        fig.set_yaxis_title("count", row=2, col=2)

        df_res = residuals.pd_dataframe()
        fig.add_scatter(x=df_res.index, y=df_res["close"], name="close", row=1, col=1)
        fig.add_corr_plot(residuals.univariate_values(), row=2, col=1)
        fig.add_histplot(residuals, row=2, col=2, bins=num_bins, forecast=True)
        fig.update_traces(showlegend=False)
        fig.update_layout(hovermode="closest")
        fig.show()


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
    if (
        target_column
        and target_column in data.columns
        and data[target_column].isin([np.inf, -np.inf]).any()
    ):
        console.print(
            f"[red]The target column [{target_column}] has inf values. Cleaning...[/red]\n"
        )
        data = data.replace([np.inf, -np.inf], np.nan)

    # check if past covariates are in data and if they have any inf
    if past_covariates:
        covariates = past_covariates.split(",")
        for covariate in covariates:
            if (
                covariate in data.columns
                and data[covariate].isin([np.inf, -np.inf]).any()
            ):
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


def print_tensorboard_logs(model_save_name: str, user_directory: str):
    console.print()
    tensorboard_logs_dir = os.path.join(user_directory, model_save_name, "logs")
    console.print(
        "This model supports Tensorboard logs. To view, open a new terminal windown and run:"
    )
    console.print("tensorboard --logdir=" + tensorboard_logs_dir)
    console.print()

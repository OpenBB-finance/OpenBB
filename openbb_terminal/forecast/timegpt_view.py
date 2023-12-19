"""Probabilistic Exponential Smoothing View"""
__docformat__ = "numpy"

import logging
import os
from datetime import datetime
from typing import List, Optional, Union

import pandas as pd
import plotly.graph_objs as go

from openbb_terminal import OpenBBFigure, theme
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.forecast import helpers, timegpt_model
from openbb_terminal.helper_funcs import export_data
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)
# pylint: disable=too-many-arguments


@log_start_end(log=logger)
@check_api_key(["API_KEY_NIXTLA"])
def display_timegpt_forecast(
    data: Union[pd.DataFrame, pd.Series],
    dataset_name: str = "",
    time_col: str = "ds",
    target_col: str = "y",
    forecast_horizon: int = 12,
    levels: Optional[List[float]] = None,
    freq: Union[str, None] = None,
    finetune_steps: int = 0,
    clean_ex_first: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    residuals: bool = False,
    date_features: Optional[List[str]] = None,
) -> Union[OpenBBFigure, None]:
    """TimeGPT was trained on the largest collection of data in history -
    over 100 billion rows of financial, weather, energy, and web data -
    and democratizes the power of time-series analysis.

    Parameters
    ----------
    data : Union[pd.Series, pd.DataFrame]
        Input data.
    dataset_name : str
        Dataset name
    time_col: str:
        Column that identifies each timestep, its values can be timestamps or integers. Defaults to "ds".
    target_column: str:
        Target column to forecast. Defaults to "y".
    forecast_horizon: int
        Number of days to forecast. Defaults to 12.
    levels: List[float]
        Confidence levels between 0 and 100 for prediction intervals.
    freq: Optional[str, None]
        Frequency of the data. By default, the freq will be inferred automatically.
    finetune_steps: int
        Number of steps used to finetune TimeGPT in the new data.
    clean_ex_first: bool
        Clean exogenous signal before making forecasts using TimeGPT.
    export: str
        Format to export data
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    external_axes: Optional[List[plt.axes]]
        External axes to plot on
    start_date: Optional[datetime]
        The starting date to perform analysis, data before this is trimmed. Defaults to None.
    end_date: Optional[datetime]
        The ending date to perform analysis, data after this is trimmed. Defaults to None.
    residuals: bool
        Whether to show residuals for the model. Defaults to False.
    date_features: Optional[List[str]]
        Specifies which date attributes have highest weight according to model.

    Returns
    -------
    pd.DataFrame
        Forecasted values.
    """
    if levels is None:
        levels = [80, 95]

    if time_col not in data.columns:
        if time_col == "ds":  # means that the user has not set it yet, bc default
            console.print(
                f"[red]Set the time column for '{dataset_name}' between: {', '.join(data.columns)}[/red]"
            )
        else:
            console.print(f"[red]Time column '{time_col}' not found in data[/red]")
        return None

    if target_col not in data.columns:
        if target_col == "y":  # means that the user has not set it yet, bc default
            console.print(
                f"[red]Set the target column for '{dataset_name}' between: {', '.join(data.columns)}[/red]"
            )
        else:
            console.print(f"[red]Target column '{target_col}' not found in data[/red]")
        return None

    data = helpers.clean_data(data, start_date, end_date, target_col, None)
    if not helpers.check_data(data, target_col, None):
        return None

    df, datefeatures_df = timegpt_model.get_timegpt_model(
        data=data,
        time_col=time_col,
        target_col=target_col,
        forecast_horizon=forecast_horizon,
        levels=levels,
        freq=freq,
        finetune_steps=finetune_steps,
        clean_ex_first=clean_ex_first,
        residuals=residuals,
        date_features=date_features,
    )

    fig = OpenBBFigure(xaxis_title="Date")

    fig.set_title(f"TimeGPT-1 (Beta) on {target_col} with horizon {forecast_horizon}")

    if residuals:
        xds = list(pd.to_datetime(df[time_col].values))[:-forecast_horizon]
        xds_reverse = list(pd.to_datetime(df[time_col].values))[:-forecast_horizon]
        xds_reverse.reverse()
        xds += xds_reverse

    xds_forecast = list(pd.to_datetime(df[time_col].values))[-forecast_horizon:]
    xds_forecast_reverse = list(pd.to_datetime(df[time_col].values))[-forecast_horizon:]
    xds_forecast_reverse.reverse()
    xds_forecast += xds_forecast_reverse

    # this is done so the confidence levels are displayed correctly
    levels.sort()
    for count, lvl in enumerate(levels):
        lvl_name = (
            str(lvl)
            if isinstance(lvl, int)
            else str(int(lvl) if lvl.is_integer() else lvl)
        )

        if residuals:
            ylo = list(df[f"TimeGPT-lo-{lvl_name}"].values)[:-forecast_horizon]
            yhigh = list(df[f"TimeGPT-hi-{lvl_name}"].values)[:-forecast_horizon]
            yhigh.reverse()
            ylo += yhigh

            fig.add_traces(
                [
                    go.Scatter(
                        x=xds,
                        y=ylo,
                        mode="lines",
                        line_color=f"rgba(255,127,14,{.2+(len(levels)-count)*(.6/(len(levels)+1))})",
                        name=f"{lvl_name}% confidence interval historical",
                        fill="toself",
                        fillcolor=f"rgba(255,127,14,{.2+(len(levels)-count)*(.6/(len(levels)+1))})",
                    )
                ]
            )

        ylo_forecast = list(df[f"TimeGPT-lo-{lvl_name}"].values)[-forecast_horizon:]
        yhigh_forecast = list(df[f"TimeGPT-hi-{lvl_name}"].values)[-forecast_horizon:]
        yhigh_forecast.reverse()
        ylo_forecast += yhigh_forecast

        fig.add_traces(
            [
                go.Scatter(
                    x=xds_forecast,
                    y=ylo_forecast,
                    mode="lines",
                    line_color=f"rgba(0,172,255,{.2+(len(levels)-count)*(.6/(len(levels)+1))})",
                    name=f"{lvl_name}% confidence interval",
                    fill="toself",
                    fillcolor=f"rgba(0,172,255,{.2+(len(levels)-count)*(.6/(len(levels)+1))})",
                )
            ]
        )

    if residuals:
        # TimeGPT prediction - historical
        fig.add_scatter(
            x=list(pd.to_datetime(df[time_col].values))[:-forecast_horizon],
            y=list(df["TimeGPT"].values)[:-forecast_horizon],
            name="TimeGPT historical forecast",
            mode="lines",
            line=dict(
                color="rgba(255,127,14,1)",
                width=3,
            ),
        )

    # TimeGPT prediction
    fig.add_scatter(
        x=list(pd.to_datetime(df[time_col].values))[-forecast_horizon:],
        y=list(df["TimeGPT"].values)[-forecast_horizon:],
        name="TimeGPT forecast",
        mode="markers+lines",
        line=dict(
            color="rgba(0,172,255,1)",
            width=3,
        ),
    )

    # Current data
    fig.add_scatter(
        x=list(pd.to_datetime(data[time_col].values)),
        y=list(data[target_col].values),
        name="Actual",
        line_color="gold",
        mode="lines",
    )
    fig.show(external=external_axes)

    if date_features:
        fig2 = OpenBBFigure(xaxis_title="Weights")

        fig2.set_title("Date features weight")

        fig2.add_bar(
            y=datefeatures_df["features"],
            x=datefeatures_df["weights"],
            marker_color=theme.up_color,
            orientation="h",
        )
        fig2.show(external=external_axes)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        f"timegpt_forecast_{target_col}",
        df=df,
        sheet_name=sheet_name,
        figure=fig,
    )

    return fig

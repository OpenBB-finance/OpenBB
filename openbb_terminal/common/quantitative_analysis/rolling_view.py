"""Rolling Statistics View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.common.quantitative_analysis import rolling_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_mean_std(
    data: pd.DataFrame,
    target: str,
    symbol: str = "",
    window: int = 14,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots mean std deviation

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe
    target: str
        Column in data to look at
    symbol : str
        Stock ticker
    window : int
        Length of window
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    data = data[target]
    rolling_mean, rolling_std = rolling_model.get_rolling_avg(data, window)
    plot_data = pd.merge(
        data,
        rolling_mean,
        how="outer",
        left_index=True,
        right_index=True,
        suffixes=("", "_mean"),
    )
    plot_data = pd.merge(
        plot_data,
        rolling_std,
        how="outer",
        left_index=True,
        right_index=True,
        suffixes=("", "_std"),
    )

    fig = OpenBBFigure.create_subplots(
        2,
        1,
        shared_xaxes=True,
        subplot_titles=[
            f"Rolling mean and std (window {str(window)}) of {symbol} {target}"
        ],
        vertical_spacing=0.1,
    )
    fig.add_scatter(
        x=plot_data.index,
        y=plot_data[target].values,
        name="Real Values",
        legend="legend",
        row=1,
        col=1,
    )
    fig.add_scatter(
        x=plot_data.index,
        y=plot_data[target + "_mean"].values,
        name="Rolling Mean",
        legend="legend",
        row=1,
        col=1,
    )
    fig.add_scatter(
        x=plot_data.index,
        y=plot_data[target + "_std"].values,
        name="Rolling Std",
        legend="legend2",
        row=2,
        col=1,
    )
    fig.update_layout(
        legend=dict(xref="paper", yref="paper"),
        legend2=dict(
            xanchor="left",
            yanchor="top",
            xref="paper",
            yref="paper",
            x=0.01,
            y=0.44,
        ),
        yaxis=dict(title="Values"),
        yaxis2=dict(title=f"{target} Std Deviation"),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "rolling",
        rolling_mean.join(rolling_std, lsuffix="_mean", rsuffix="_std"),
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_spread(
    data: pd.DataFrame,
    target: str,
    symbol: str = "",
    window: int = 14,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots rolling spread

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe
    target: str
        Column in data to look at
    target: str
        Column in data to look at
    symbol : str
        Stock ticker
    window : int
        Length of window
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    data = data[target]
    df_sd, df_var = rolling_model.get_spread(data, window)

    plot_data = pd.merge(
        data,
        df_sd,
        how="outer",
        left_index=True,
        right_index=True,
        suffixes=("", "_sd"),
    )
    plot_data = pd.merge(
        plot_data,
        df_var,
        how="outer",
        left_index=True,
        right_index=True,
        suffixes=("", "_var"),
    )

    fig = OpenBBFigure.create_subplots(
        3,
        1,
        shared_xaxes=True,
        subplot_titles=[
            "Real Values",
            "Rolling Stdev",
            "Rolling Variance",
        ],
        vertical_spacing=0.1,
    ).set_title(f"Spread of {symbol} {target}")

    fig.add_scatter(
        x=plot_data.index,
        y=plot_data[target].values,
        name="Real Values",
        row=1,
        col=1,
    )
    fig.add_scatter(
        x=plot_data.index,
        y=plot_data[f"STDEV_{window}"].values,
        name="Rolling Stdev",
        row=2,
        col=1,
    )
    fig.add_scatter(
        x=plot_data.index,
        y=plot_data[f"VAR_{window}"].values,
        name="Rolling Variance",
        row=3,
        col=1,
    )
    fig.update_layout(
        yaxis=dict(title="Values"),
        yaxis2=dict(title="Stdev"),
        yaxis3=dict(title="Variance"),
    )
    fig.update_traces(showlegend=False)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "spread",
        df_sd.join(df_var, lsuffix="_sd", rsuffix="_var"),
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_quantile(
    data: pd.DataFrame,
    target: str,
    symbol: str = "",
    window: int = 14,
    quantile: float = 0.5,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots rolling quantile

    Parameters
    ----------
    data: pd.DataFrame
        Dataframe
    target: str
        Column in data to look at
    symbol : str
        Stock ticker
    window : int
        Length of window
    quantile: float
        Quantile to get
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes: bool, optional
        Whether to return the figure object or not, by default False
    """
    data = data[target]
    df_med, df_quantile = rolling_model.get_quantile(data, window, quantile)

    plot_data = pd.merge(
        data,
        df_med,
        how="outer",
        left_index=True,
        right_index=True,
        suffixes=("", "_med"),
    )
    plot_data = pd.merge(
        plot_data,
        df_quantile,
        how="outer",
        left_index=True,
        right_index=True,
        suffixes=("", "_quantile"),
    )

    fig = OpenBBFigure().set_title(f"{symbol} {target} Median & Quantile")

    fig.add_scatter(
        x=plot_data.index,
        y=plot_data[target].values,
        name=target,
    )
    fig.add_scatter(
        x=plot_data.index,
        y=plot_data[f"MEDIAN_{window}"].values,
        name=f"Median w={window}",
    )
    fig.add_scatter(
        x=plot_data.index,
        y=plot_data[f"QTL_{window}_{quantile}"].values,
        name=f"Quantile q={quantile}",
        line=dict(dash="dash"),
    )
    fig.update_layout(yaxis=dict(title=f"{symbol} Value"))

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "quantile",
        df_med.join(df_quantile),
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_skew(
    symbol: str,
    data: pd.DataFrame,
    target: str,
    window: int = 14,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots rolling skew

    Parameters
    ----------
    symbol: str
        Stock ticker
    data: pd.DataFrame
        Dataframe
    target: str
        Column in data to look at
    window: int
        Length of window
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    data = data[target]
    df_skew = rolling_model.get_skew(data, window)

    plot_data = pd.merge(
        data,
        df_skew,
        how="outer",
        left_index=True,
        right_index=True,
    )

    fig = OpenBBFigure.create_subplots(
        rows=2,
        cols=1,
        vertical_spacing=0.1,
    ).set_title(f"{symbol} Skewness Indicator")

    fig.add_scatter(
        x=plot_data.index,
        y=plot_data[target].values,
        name=target,
        row=1,
        col=1,
    )

    fig.add_scatter(
        x=plot_data.index,
        y=plot_data[f"SKEW_{window}"].values,
        name=f"Skew w={window}",
        row=2,
        col=1,
    )

    fig.update_layout(yaxis=dict(title=f"{target}"), yaxis2=dict(title="Indicator"))

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "skew",
        df_skew,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)


@log_start_end(log=logger)
def display_kurtosis(
    symbol: str,
    data: pd.DataFrame,
    target: str,
    window: int = 14,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Plots rolling kurtosis

    Parameters
    ----------
    symbol: str
        Ticker
    data: pd.DataFrame
        Dataframe of stock prices
    target: str
        Column in data to look at
    window: int
        Length of window
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    data = data[target]
    df_kurt = rolling_model.get_kurtosis(data, window)

    plot_data = pd.merge(
        data,
        df_kurt,
        how="outer",
        left_index=True,
        right_index=True,
    )

    fig = OpenBBFigure.create_subplots(
        rows=2,
        cols=1,
        vertical_spacing=0.1,
        subplot_titles=[f"{target}", "Kurtosis"],
    ).set_title(f"{symbol} {target} Kurtosis Indicator (window {str(window)})")

    fig.add_scatter(
        x=plot_data.index,
        y=plot_data[target].values,
        name=target,
        row=1,
        col=1,
    )

    fig.add_scatter(
        x=plot_data.index,
        y=plot_data[f"KURT_{window}"].values,
        name=f"Kurtosis w={window}",
        row=2,
        col=1,
    )

    fig.update_layout(yaxis=dict(title=f"{target}"), yaxis2=dict(title="Indicator"))
    fig.update_traces(showlegend=False)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "kurtosis",
        df_kurt,
        sheet_name,
        fig,
    )

    return fig.show(external=external_axes)

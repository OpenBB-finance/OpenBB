"""Rolling Statistics View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, List

import matplotlib.pyplot as plt
import pandas as pd

from openbb_terminal.config_terminal import theme
from openbb_terminal.common.quantitative_analysis import rolling_model
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, plot_autoscale, reindex_dates
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_mean_std(
    name: str,
    df: pd.DataFrame,
    target: str,
    window: int,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """View rolling spread

    Parameters
    ----------
    name : str
        Stock ticker
    df : pd.DataFrame
        Dataframe
    target : str
        Column in data to look at
    window : int
        Length of window
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    data = df[target]
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
    plot_data = reindex_dates(plot_data)

    # This plot has 2 axes
    if external_axes is None:
        _, axes = plt.subplots(
            2,
            1,
            sharex=True,
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
        ax1, ax2 = axes
    else:
        if len(external_axes) != 2:
            logger.error("Expected list of two axis items.")
            console.print("[red]Expected list of 2 axis items./n[/red]")
            return
        (ax1, ax2) = external_axes

    ax1.plot(
        plot_data.index,
        plot_data[target].values,
        label=name,
    )
    ax1.plot(
        plot_data.index,
        plot_data[target + "_mean"].values,
    )
    ax1.set_ylabel(
        "Values",
    )
    ax1.legend(["Real Values", "Rolling Mean"])
    ax1.set_title(f"Rolling mean and std (window {str(window)}) of {name} {target}")
    ax1.set_xlim([plot_data.index[0], plot_data.index[-1]])

    ax2.plot(
        plot_data.index,
        plot_data[target + "_std"].values,
        label="Rolling std",
    )
    ax2.legend(["Rolling std"])
    ax2.set_ylabel(
        f"{target} Std Deviation",
    )

    theme.style_primary_axis(
        ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )
    theme.style_primary_axis(
        ax2,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "rolling",
        rolling_mean.join(rolling_std, lsuffix="_mean", rsuffix="_std"),
    )


@log_start_end(log=logger)
def display_spread(
    name: str,
    df: pd.DataFrame,
    target: str,
    window: int,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """View rolling spread

    Parameters
    ----------
    name : str
        Stock ticker
    df : pd.DataFrame
        Dataframe
    target: str
        Column in data to look at
    window : int
        Length of window
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
    """
    data = df[target]
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
    plot_data = reindex_dates(plot_data)

    # This plot has 1 axis
    if external_axes is None:
        _, axes = plt.subplots(
            3,
            1,
            sharex=True,
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
        (ax1, ax2, ax3) = axes
    else:
        if len(external_axes) != 3:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of 1 axis items./n[/red]")
            return
        (ax1, ax2, ax3) = external_axes

    ax1.plot(plot_data.index, plot_data[target].values)
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel("Value")
    ax1.set_title(f"Spread of {name} {target}")

    ax2.plot(
        plot_data[f"STDEV_{window}"].index,
        plot_data[f"STDEV_{window}"].values,
        label="Stdev",
    )
    ax2.set_ylabel("Stdev")

    ax3.plot(
        plot_data[f"VAR_{window}"].index,
        plot_data[f"VAR_{window}"].values,
        label="Variance",
    )
    ax3.set_ylabel("Variance")

    theme.style_primary_axis(
        ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )
    theme.style_primary_axis(
        ax2,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )
    theme.style_primary_axis(
        ax3,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "spread",
        df_sd.join(df_var, lsuffix="_sd", rsuffix="_var"),
    )


@log_start_end(log=logger)
def display_quantile(
    name: str,
    df: pd.DataFrame,
    target: str,
    window: int,
    quantile: float,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """View rolling quantile

    Parameters
    ----------
    name : str
        Stock ticker
    df : pd.DataFrame
        Dataframe
    target : str
        Column in data to look at
    window : int
        Length of window
    quantile : float
        Quantile to get
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    data = df[target]
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
    plot_data = reindex_dates(plot_data)

    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of 1 axis items./n[/red]")
            return
        (ax,) = external_axes

    ax.set_title(f"{name} {target} Median & Quantile")
    ax.plot(plot_data.index, plot_data[target].values, label=target)
    ax.plot(
        plot_data.index,
        plot_data[f"MEDIAN_{window}"].values,
        label=f"Median w={window}",
    )
    ax.plot(
        plot_data.index,
        plot_data[f"QTL_{window}_{quantile}"].values,
        label=f"Quantile q={quantile}",
        linestyle="--",
    )

    ax.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax.set_ylabel(f"{name} Value")
    ax.legend()

    theme.style_primary_axis(
        ax,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "quantile",
        df_med.join(df_quantile),
    )


@log_start_end(log=logger)
def display_skew(
    name: str,
    df: pd.DataFrame,
    target: str,
    window: int,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """View rolling skew

    Parameters
    ----------
    name : str
        Stock ticker
    df : pd.DataFrame
        Dataframe
    target : str
        Column in data to look at
    window : int
        Length of window
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    data = df[target]
    df_skew = rolling_model.get_skew(data, window)

    plot_data = pd.merge(
        data,
        df_skew,
        how="outer",
        left_index=True,
        right_index=True,
    )
    plot_data = reindex_dates(plot_data)

    # This plot has 1 axis
    if external_axes is None:
        _, axes = plt.subplots(
            2,
            1,
            sharex=True,
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
        (ax1, ax2) = axes
    else:
        if len(external_axes) != 2:
            logger.error("Expected list of two axis items.")
            console.print("[red]Expected list of 2 axis items./n[/red]")
            return
        (ax1, ax2) = external_axes

    ax1.set_title(f"{name} Skewness Indicator")
    ax1.plot(plot_data.index, plot_data[target].values)
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel(f"{target}")

    ax2.plot(plot_data.index, plot_data[f"SKEW_{window}"].values, label="Skew")
    ax2.set_ylabel("Indicator")

    theme.style_primary_axis(
        ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )
    theme.style_primary_axis(
        ax2,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    if external_axes is None:
        theme.visualize_output()

    console.print("")
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "skew",
        df_skew,
    )


@log_start_end(log=logger)
def display_kurtosis(
    name: str,
    df: pd.DataFrame,
    target: str,
    window: int,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """View rolling kurtosis

    Parameters
    ----------
    name : str
        Ticker
    df : pd.DataFrame
        Dataframe of stock prices
    window : int
        Length of window
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    data = df[target]
    df_kurt = rolling_model.get_kurtosis(data, window)

    plot_data = pd.merge(
        data,
        df_kurt,
        how="outer",
        left_index=True,
        right_index=True,
    )
    plot_data = reindex_dates(plot_data)

    # This plot has 1 axis
    if external_axes is None:
        _, axes = plt.subplots(
            2,
            1,
            sharex=True,
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
        (ax1, ax2) = axes
    else:
        if len(external_axes) != 2:
            logger.error("Expected list of two axis items.")
            console.print("[red]Expected list of 2 axis items./n[/red]")
            return
        (ax1, ax2) = external_axes

    ax1.set_title(f"{name} {target} Kurtosis Indicator (window {str(window)})")
    ax1.plot(plot_data.index, plot_data[target].values)
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel(f"{target}")

    ax2.plot(
        plot_data.index,
        plot_data[f"KURT_{window}"].values,
    )
    ax2.set_ylabel("Indicator")

    theme.style_primary_axis(
        ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )
    theme.style_primary_axis(
        ax2,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    if external_axes is None:
        theme.visualize_output()

    console.print("")
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "kurtosis",
        df_kurt,
    )

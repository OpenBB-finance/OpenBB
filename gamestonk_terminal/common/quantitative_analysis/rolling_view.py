"""Rolling Statistics View"""
__docformat__ = "numpy"

import logging
import os

import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.common.quantitative_analysis import rolling_model
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def display_mean_std(
    name: str, df: pd.DataFrame, target: str, length: int, export: str = ""
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
    length : int
        Length of window
    export : str
        Format to export data
    """
    data = df[target]
    rolling_mean, rolling_std = rolling_model.get_rolling_avg(data, length)
    fig, axMean = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    axMean.plot(
        data.index,
        data.values,
        label=name,
        linewidth=2,
        color="black",
    )
    axMean.plot(rolling_mean, linestyle="--", linewidth=3, color="blue")
    axMean.set_xlabel("Time")
    axMean.set_ylabel("Values", color="blue")
    axMean.legend(["Real values", "Rolling Mean"], loc=2)
    axMean.tick_params(axis="y", labelcolor="blue")
    axStd = axMean.twinx()
    axStd.plot(
        rolling_std,
        label="Rolling std",
        linestyle="--",
        color="green",
        linewidth=3,
        alpha=0.6,
    )
    axStd.set_ylabel("Std Deviation")
    axStd.legend(["Rolling std"], loc=1)
    axStd.set_ylabel(f"{target} standard deviation", color="green")
    axStd.tick_params(axis="y", labelcolor="green")
    axMean.set_title(
        "Rolling mean and std with window "
        + str(length)
        + " applied to "
        + name
        + target
    )
    axMean.set_xlim([data.index[0], data.index[-1]])
    axMean.grid(b=True, which="major", color="#666666", linestyle="-")

    if gtff.USE_ION:
        plt.ion()
    fig.tight_layout(pad=1)
    plt.gcf().autofmt_xdate()
    plt.show()
    console.print("")
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "rolling",
        rolling_mean.join(rolling_std, lsuffix="_mean", rsuffix="_sd"),
    )


@log_start_end(log=logger)
def display_spread(
    name: str, df: pd.DataFrame, target: str, length: int, export: str = ""
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
    length : int
        Length of window
    export : str
        Format to export data
    """
    data = df[target]
    df_sd, df_var = rolling_model.get_spread(data, length)
    fig, axes = plt.subplots(3, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax = axes[0]
    ax.set_title(f"{name} Spread")
    ax.plot(data.index, data.values, "fuchsia", lw=1)
    ax.set_xlim(data.index[0], data.index[-1])
    ax.set_ylabel("Value")
    ax.set_title(f"Spread of {name} {target}")
    ax.yaxis.set_label_position("right")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")
    ax.minorticks_on()
    ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    ax1 = axes[1]
    ax1.plot(df_sd.index, df_sd.values, "b", lw=1, label="stdev")
    ax1.set_xlim(data.index[0], data.index[-1])
    ax1.set_ylabel("Stdev")
    ax1.yaxis.set_label_position("right")
    ax1.grid(b=True, which="major", color="#666666", linestyle="-")
    ax1.minorticks_on()
    ax1.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    ax2 = axes[2]
    ax2.plot(df_var.index, df_var.values, "g", lw=1, label="variance")
    ax2.set_xlim(data.index[0], data.index[-1])
    ax2.set_ylabel("Variance")
    ax2.yaxis.set_label_position("right")
    ax2.grid(b=True, which="major", color="#666666", linestyle="-")

    if gtff.USE_ION:
        plt.ion()

    plt.gcf().autofmt_xdate()
    fig.tight_layout(pad=1)
    plt.show()
    console.print("")
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
    length: int,
    quantile: float,
    export: str = "",
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
    length : int
        Length of window
    quantle : float
        Quantil eto get
    export : str
        Format to export data
    """
    data = df[target]
    df_med, df_quantile = rolling_model.get_quantile(data, length, quantile)
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax.plot(data.index, data.values, color="fuchsia")
    ax.set_title(f"{name} Median & Quantile")
    ax.plot(df_med.index, df_med.values, "g", lw=1, label="median")
    ax.plot(df_quantile.index, df_quantile.values, "b", lw=1, label="quantile")

    ax.set_title(f"Median & Quantile on {name}")
    ax.set_xlim(data.index[0], data.index[-1])
    ax.set_xlabel("Time")
    ax.set_ylabel(f"{name} Value")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")

    if gtff.USE_ION:
        plt.ion()

    plt.gcf().autofmt_xdate()
    fig.tight_layout(pad=1)

    plt.legend()
    plt.show()
    console.print("")
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "quantile",
        df_med.join(df_quantile),
    )


@log_start_end(log=logger)
def display_skew(
    name: str, df: pd.DataFrame, target: str, length: int, export: str = ""
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
    length : int
        Length of window
    export : str
        Format to export data
    """
    data = df[target]
    df_skew = rolling_model.get_skew(data, length)
    fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax = axes[0]
    ax.set_title(f"{name} Skewness Indicator")
    ax.plot(data.index, data.values, "fuchsia", lw=1)
    ax.set_xlim(data.index[0], data.index[-1])
    ax.set_ylabel(f"{target}")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")
    ax.minorticks_on()
    ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    ax2 = axes[1]
    ax2.plot(df_skew.index, df_skew.values, "b", lw=2, label="skew")

    ax2.set_xlim(data.index[0], data.index[-1])
    ax2.grid(b=True, which="major", color="#666666", linestyle="-")

    if gtff.USE_ION:
        plt.ion()

    plt.gcf().autofmt_xdate()
    fig.tight_layout(pad=1)

    plt.legend()
    plt.show()

    console.print("")
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "skew",
        df_skew,
    )


@log_start_end(log=logger)
def display_kurtosis(
    name: str, df: pd.DataFrame, target: str, length: int, export: str = ""
):
    """View rolling kurtosis

    Parameters
    ----------
    name : str
        Ticker
    df : pd.DataFrame
        Dataframe of stock prices
    length : int
        Length of window
    export : str
        Format to export data
    """
    data = df[target]
    df_kurt = rolling_model.get_kurtosis(data, length)
    fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax = axes[0]
    ax.set_title(f"{name} Kurtosis Indicator")
    ax.plot(data.index, data.values, "fuchsia", lw=1)
    ax.set_xlim(data.index[0], data.index[-1])
    ax.set_ylabel(f"{target}")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")
    ax.minorticks_on()
    ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    ax2 = axes[1]
    ax2.plot(df_kurt.index, df_kurt.values, "b", lw=2, label="kurtosis")

    ax2.set_xlim(df.index[0], df.index[-1])
    ax2.grid(b=True, which="major", color="#666666", linestyle="-")

    if gtff.USE_ION:
        plt.ion()

    plt.gcf().autofmt_xdate()
    fig.tight_layout(pad=1)

    plt.legend()
    plt.show()

    console.print("")
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "kurtosis",
        df_kurt,
    )

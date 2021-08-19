"""Rolling Statistics View"""
__docformat__ = "numpy"

import os
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
from gamestonk_terminal.helper_funcs import plot_autoscale, export_data
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.common.quantitative_analysis import rolling_model


register_matplotlib_converters()


def view_spread(
    s_ticker: str, s_interval: str, df_stock: pd.DataFrame, length: int, export: str
):
    """View rolling spread

    Parameters
    ----------
    s_ticker : str
        Stock ticker
    s_interval : str
        Interval of data
    df_stock : pd.DataFrame
        Dataframe of stock prices
    length : int
        Length of window
    export : str
        Format to export data
    """
    df_sd, df_var = rolling_model.spread(s_interval, df_stock, length)
    fig, axes = plt.subplots(3, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax = axes[0]
    ax.set_title(f"{s_ticker} Spread")
    if s_interval == "1440min":
        ax.plot(df_stock.index, df_stock["Adj Close"].values, "fuchsia", lw=1)
    else:
        ax.plot(df_stock.index, df_stock["Close"].values, "fuchsia", lw=1)
    ax.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax.set_ylabel("Price")
    ax.yaxis.set_label_position("right")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")
    ax.minorticks_on()
    ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    ax1 = axes[1]
    ax1.plot(df_sd.index, df_sd.values, "b", lw=1, label="stdev")
    ax1.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax1.set_ylabel("Stdev")
    ax1.yaxis.set_label_position("right")
    ax1.grid(b=True, which="major", color="#666666", linestyle="-")
    ax1.minorticks_on()
    ax1.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    ax2 = axes[2]
    ax2.plot(df_var.index, df_var.values, "g", lw=1, label="variance")
    ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax2.set_ylabel("Variance")
    ax2.yaxis.set_label_position("right")
    ax2.grid(b=True, which="major", color="#666666", linestyle="-")

    if gtff.USE_ION:
        plt.ion()

    plt.gcf().autofmt_xdate()
    fig.tight_layout(pad=1)
    plt.show()
    print("")
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "spread",
        df_sd.join(df_var),
    )


def view_quantile(
    s_ticker: str,
    s_interval: str,
    df_stock: pd.DataFrame,
    length: int,
    quantile: float,
    export: str,
):
    """View rolling quantile

    Parameters
    ----------
    s_ticker : str
        Stock ticker
    s_interval : str
        Interval of data
    df_stock : pd.DataFrame
        Dataframe of stock prices
    length : int
        Length of window
    quantle : float
        Quantil eto get
    export : str
        Format to export data
    """
    df_med, df_quantile = rolling_model.quantile(s_interval, df_stock, length, quantile)
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    if s_interval == "1440min":
        ax.plot(df_stock.index, df_stock["Adj Close"].values, color="fuchsia")
    else:
        ax.plot(df_stock.index, df_stock["Close"].values, color="fuchsia")
    ax.set_title(f"{s_ticker} Median & Quantile")

    ax.plot(df_med.index, df_med.values, "g", lw=1, label="median")
    ax.plot(df_quantile.index, df_quantile.values, "b", lw=1, label="quantile")

    ax.set_title(f"Median & Quantile on {s_ticker}")
    ax.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax.set_xlabel("Time")
    ax.set_ylabel(f"{s_ticker} Price ($)")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")

    if gtff.USE_ION:
        plt.ion()

    plt.gcf().autofmt_xdate()
    fig.tight_layout(pad=1)

    plt.legend()
    plt.show()
    print("")
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "quantile",
        df_med.join(df_quantile),
    )


def view_skew(
    s_ticker: str, s_interval: str, df_stock: pd.DataFrame, length: int, export: str
):
    """View rolling skew

    Parameters
    ----------
    s_ticker : str
        Stock ticker
    s_interval : str
        Interval of data
    df_stock : pd.DataFrame
        Dataframe of stock prices
    length : int
        Length of window
    export : str
        Format to export data
    """
    df_skew = rolling_model.skew(s_interval, df_stock, length)
    fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax = axes[0]
    ax.set_title(f"{s_ticker} Skewness Indicator")
    if s_interval == "1440min":
        ax.plot(df_stock.index, df_stock["Adj Close"].values, "fuchsia", lw=1)
    else:
        ax.plot(df_stock.index, df_stock["Close"].values, "fuchsia", lw=1)
    ax.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax.set_ylabel("Share Price ($)")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")
    ax.minorticks_on()
    ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    ax2 = axes[1]
    ax2.plot(df_skew.index, df_skew.values, "b", lw=2, label="skew")

    ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax2.grid(b=True, which="major", color="#666666", linestyle="-")

    if gtff.USE_ION:
        plt.ion()

    plt.gcf().autofmt_xdate()
    fig.tight_layout(pad=1)

    plt.legend()
    plt.show()

    print("")
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "skew",
        df_skew,
    )

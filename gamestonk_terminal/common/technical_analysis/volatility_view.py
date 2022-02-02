"""Volatility Technical Indicators View"""
__docformat__ = "numpy"

import logging
import os

import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.common.technical_analysis import volatility_model
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def display_bbands(
    df_stock: pd.DataFrame,
    length: int = 15,
    n_std: float = 2,
    mamode: str = "sma",
    ticker: str = "",
    export: str = "",
):
    """Show bollinger bands

    Parameters
    ----------
    ticker : str
        Ticker
    df_stock : pd.DataFrame
        Dataframe of stock prices
    length : int
        Length of window to calculate BB
    n_std : float
        Number of standard deviations to show
    mamode : str
        Method of calculating average
    s_interval : str
        Interval of stock data
    export : str
        Format of export file
    """
    df_ta = volatility_model.bbands(df_stock["Adj Close"], length, n_std, mamode)

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax.plot(
        df_stock.index,
        df_stock["Adj Close"].values,
    )
    ax.plot(df_ta.index, df_ta.iloc[:, 0].values, theme.down_color, linewidth=0.7)
    ax.plot(df_ta.index, df_ta.iloc[:, 1].values, ls="--", linewidth=0.7)
    ax.plot(df_ta.index, df_ta.iloc[:, 2].values, theme.up_color, linewidth=0.7)
    ax.set_title(f"{ticker} Bollinger Bands")
    ax.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax.set_ylabel("Share Price ($)")
    ax.yaxis.set_label_position("right")
    ax.grid(visible=True, zorder=0)
    ax.tick_params(axis="x", rotation=10)

    ax.legend([ticker, df_ta.columns[0], df_ta.columns[1], df_ta.columns[2]])
    ax.fill_between(
        df_ta.index, df_ta.iloc[:, 0].values, df_ta.iloc[:, 2].values, alpha=0.1
    )

    if gtff.USE_ION:
        plt.ion()
    fig.tight_layout(pad=1)
    plt.show()
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "bbands",
        df_ta,
    )


@log_start_end(log=logger)
def display_donchian(
    df_stock: pd.DataFrame,
    upper_length: int = 20,
    lower_length: int = 20,
    ticker: str = "",
    export: str = "",
):
    """Show donchian channels

    Parameters
    ----------
    ticker : str
        Ticker
    df_stock : pd.DataFrame
        Dataframe of stock prices
    upper_length : int
        Length of window to calculate upper channel
    lower_length : int
        Length of window to calculate lower channel
    s_interval : str
        Interval of stock data
    export : str
        Format of export file
    """
    df_ta = volatility_model.donchian(
        df_stock["High"], df_stock["Low"], upper_length, lower_length
    )

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax.plot(df_stock.index, df_stock["Adj Close"].values)
    ax.plot(df_ta.index, df_ta.iloc[:, 0].values, linewidth=0.7, label="Upper")
    ax.plot(df_ta.index, df_ta.iloc[:, 1].values, linewidth=0.7, ls="--")
    ax.plot(df_ta.index, df_ta.iloc[:, 2].values, linewidth=0.7, label="Lower")
    ax.set_title(f"{ticker} donchian")
    ax.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax.set_ylabel("Price ($)")
    ax.yaxis.set_label_position("right")
    ax.grid(visible=True, zorder=0)
    ax.tick_params(axis="x", rotation=10)

    ax.legend([ticker, df_ta.columns[0], df_ta.columns[1], df_ta.columns[2]])
    ax.fill_between(
        df_ta.index, df_ta.iloc[:, 0].values, df_ta.iloc[:, 2].values, alpha=0.1
    )

    if gtff.USE_ION:
        plt.ion()

    fig.tight_layout(pad=1)
    plt.legend()
    plt.show()
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "donchian",
        df_ta,
    )


@log_start_end(log=logger)
def view_kc(
    df_stock: pd.DataFrame,
    length: int = 20,
    scalar: float = 2,
    mamode: str = "ema",
    offset: int = 0,
    s_ticker: str = "",
    export: str = "",
):
    """View Keltner Channels Indicator

    Parameters
    ----------

    df_stock : pd.DataFrame
        Dataframe of stock prices
    length : int
        Length of window
    mamode: str
        Type of filter
    offset : int
        Offset value
    s_ticker : str
        Ticker
    export : str
        Format to export data
    """
    df_ta = volatility_model.kc(
        df_stock["High"],
        df_stock["Low"],
        df_stock["Adj Close"],
        length,
        scalar,
        mamode,
        offset,
    )
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax.plot(df_stock.index, df_stock["Adj Close"].values)
    ax.plot(df_ta.index, df_ta.iloc[:, 0].values, linewidth=0.7, label="Upper")
    ax.plot(df_ta.index, df_ta.iloc[:, 1].values, linewidth=0.7, ls="--")
    ax.plot(df_ta.index, df_ta.iloc[:, 2].values, linewidth=0.7, label="Lower")
    ax.set_title(f"{s_ticker} Keltner Channels")
    ax.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax.set_ylabel("Price")
    ax.yaxis.set_label_position("right")
    ax.grid(visible=True, zorder=0)
    ax.tick_params(axis="x", rotation=10)

    ax.legend([s_ticker, df_ta.columns[0], df_ta.columns[1], df_ta.columns[2]])
    ax.fill_between(
        df_ta.index, df_ta.iloc[:, 0].values, df_ta.iloc[:, 2].values, alpha=0.1
    )

    if gtff.USE_ION:
        plt.ion()
    fig.tight_layout(pad=1)
    plt.legend()
    plt.show()

    console.print("")
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "kc",
        df_ta,
    )

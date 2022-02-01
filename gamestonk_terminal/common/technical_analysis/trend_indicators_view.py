"""Trend Indicators View"""
__docformat__ = "numpy"

import logging
import os

import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.common.technical_analysis import trend_indicators_model
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def display_adx(
    df_stock: pd.DataFrame,
    length: int = 14,
    scalar: int = 100,
    drift: int = 1,
    s_ticker: str = "",
    export: str = "",
):
    """Plot ADX indicator

    Parameters
    ----------
    df_stock
        Dataframe of prices
    length : int
        Length of window
    scalar : int
        Scalar variable
    drift : int
        Drift variable
    s_ticker : str
        Ticker
    export: str
        Format to export data
    """
    df_ta = trend_indicators_model.adx(
        high_values=df_stock["High"],
        low_values=df_stock["Low"],
        close_values=df_stock["Adj Close"],
        length=length,
        scalar=scalar,
        drift=drift,
    )

    fig, ax = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax0 = ax[0]
    ax0.plot(df_stock.index, df_stock["Close"].values, "k", lw=2)
    ax0.set_title(f"Average Directional Movement Index (ADX) on {s_ticker}")
    ax0.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax0.set_ylabel("Share Price ($)")
    ax0.grid(b=True, which="major", color="#666666", linestyle="-")

    ax1 = ax[1]
    ax1.plot(df_ta.index, df_ta.iloc[:, 0].values, "b", lw=2)
    ax1.plot(df_ta.index, df_ta.iloc[:, 1].values, "g", lw=1)
    ax1.plot(df_ta.index, df_ta.iloc[:, 2].values, "r", lw=1)
    ax1.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax1.axhline(25, linewidth=3, color="k", ls="--")
    ax1.legend(
        [
            f"ADX ({df_ta.columns[0]})",
            f"+DI ({df_ta.columns[1]})",
            f"- DI ({df_ta.columns[2]})",
        ],
        loc="upper left",
    )
    ax1.set_xlabel("Time")
    ax1.grid(b=True, which="major", color="#666666", linestyle="-")

    ax1.set_ylim([0, 100])

    if gtff.USE_ION:
        plt.ion()
    fig.tight_layout()
    plt.gcf().autofmt_xdate()

    plt.show()
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "adx",
        df_ta,
    )


@log_start_end(log=logger)
def display_aroon(
    df_stock: pd.DataFrame,
    length: int = 25,
    scalar: int = 100,
    s_ticker: str = "",
    export: str = "",
):
    """Plot Aroon indicator

    Parameters
    ----------
    df_stock : pd.DataFrame.length
        Dataframe of prices
    length:int
        Length of window
    s_ticker : str
        Ticker
    scalar : int
        Scalar variable
    """
    df_ta = trend_indicators_model.aroon(
        high_values=df_stock["High"],
        low_values=df_stock["Low"],
        length=length,
        scalar=scalar,
    )

    fig, ax = plt.subplots(3, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax0 = ax[0]
    # Daily
    ax0.plot(df_stock.index, df_stock["Adj Close"].values, "k", lw=2)

    ax0.set_title(f"Aroon on {s_ticker}")
    ax0.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax0.set_ylabel("Share Price ($)")
    ax0.grid(b=True, which="major", color="#666666", linestyle="-")

    ax1 = ax[1]
    ax1.plot(df_ta.index, df_ta.iloc[:, 0].values, "r", lw=2)
    ax1.plot(df_ta.index, df_ta.iloc[:, 1].values, "g", lw=2)
    ax1.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax1.axhline(50, linewidth=1, color="k", ls="--")
    ax1.legend(
        [f"Aroon DOWN ({df_ta.columns[0]})", f"Aroon UP ({df_ta.columns[1]})"],
        loc="upper left",
    )
    ax1.grid(b=True, which="major", color="#666666", linestyle="-")
    ax1.set_ylim([0, 100])

    ax2 = ax[2]
    ax2.plot(df_ta.index, df_ta.iloc[:, 2].values, "b", lw=2)
    ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax2.set_xlabel("Time")
    ax2.legend([f"Aroon OSC ({df_ta.columns[2]})"], loc="upper left")
    ax2.grid(b=True, which="major", color="#666666", linestyle="-")
    ax2.set_ylim([-100, 100])

    if gtff.USE_ION:
        plt.ion()

    fig.tight_layout(pad=1)
    plt.show()
    plt.gcf().autofmt_xdate()

    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "aroon",
        df_ta,
    )

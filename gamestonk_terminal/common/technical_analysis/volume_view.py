"""Volume View"""
__docformat__ = "numpy"

import os

import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.common.technical_analysis import volume_model
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale

register_matplotlib_converters()


def display_ad(
    df_stock: pd.DataFrame,
    use_open: bool = False,
    s_ticker: str = "",
    export: str = "",
):
    """Plot AD technical indicator

    Parameters
    ----------
    df_stock : pd.DataFrame
        Dataframe of prices
    use_open : bool
        Whether to use open prices in calculation
    s_ticker : str
        Ticker
    export: str
        Format to export data as
    """

    bar_colors = ["r" if x[1].Open < x[1].Close else "g" for x in df_stock.iterrows()]
    bar_width = df_stock.index[1] - df_stock.index[0]
    divisor = 1_000_000
    df_vol = df_stock["Volume"].dropna()
    df_vol = df_vol.values / divisor
    df_ta = volume_model.ad(df_stock, use_open)
    df_cal = df_ta.values
    df_cal = df_cal / divisor

    fig, axes = plt.subplots(
        3,
        1,
        gridspec_kw={"height_ratios": [2, 1, 1]},
        figsize=plot_autoscale(),
        dpi=PLOT_DPI,
    )
    ax = axes[0]
    ax.plot(df_stock.index, df_stock["Adj Close"].values, "k", lw=2)
    ax.set_title(f"{s_ticker} AD")
    ax.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax.set_ylabel("Price")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")

    ax2 = axes[1]
    ax2.set_ylabel("Volume [M]")

    ax2.bar(
        df_stock.index,
        df_vol,
        color=bar_colors,
        alpha=0.8,
        width=bar_width,
    )
    ax2.set_xlim(df_stock.index[0], df_stock.index[-1])

    ax3 = axes[2]
    ax3.set_ylabel("A/D [M]")
    ax3.set_xlabel("Time")
    ax3.plot(df_ta.index, df_cal, "b", lw=1)
    ax3.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax3.axhline(0, linewidth=2, color="k", ls="--")
    ax3.grid(b=True, which="major", color="#666666", linestyle="-")

    if gtff.USE_ION:
        plt.ion()

    plt.gcf().autofmt_xdate()
    fig.tight_layout(pad=1)

    plt.show()
    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "ad",
        df_ta,
    )


def display_adosc(
    df_stock: pd.DataFrame,
    fast: int = 3,
    slow: int = 10,
    use_open: bool = False,
    s_ticker: str = "",
    export: str = "",
):
    """Display AD Osc Indicator

    Parameters
    ----------
    df_stock : pd.DataFrame
        Dataframe of prices
    use_open : bool
        Whether to use open prices in calculation
    fast: int
         Length of fast window
    slow : int
        Length of slow window
    s_ticker : str
        Stock ticker
    export : str
        Format to export data
    """
    bar_colors = ["r" if x[1].Open < x[1].Close else "g" for x in df_stock.iterrows()]

    bar_width = df_stock.index[1] - df_stock.index[0]

    divisor = 1_000_000
    df_vol = df_stock["Volume"].dropna()
    df_vol = df_vol.values / divisor
    df_ta = volume_model.adosc(df_stock, use_open, fast, slow)
    df_cal = df_ta.values
    df_cal = df_cal / divisor

    fig, axes = plt.subplots(
        3,
        1,
        figsize=plot_autoscale(),
        dpi=PLOT_DPI,
    )
    ax = axes[0]
    ax.set_title(f"{s_ticker} AD Oscillator")
    ax.plot(df_stock.index, df_stock["Adj Close"].values, "fuchsia", lw=1)
    ax.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax.set_ylabel("Price")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")

    ax1 = axes[1]
    ax1.set_ylabel("Volume [M]")

    ax1.bar(
        df_stock.index,
        df_vol,
        color=bar_colors,
        alpha=0.8,
        width=bar_width,
    )
    ax1.set_xlim(df_stock.index[0], df_stock.index[-1])

    ax2 = axes[2]
    ax2.set_ylabel("AD Osc [M]")
    ax2.set_xlabel("Time")
    ax2.plot(df_ta.index, df_cal, "b", lw=2, label="AD Osc")
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
        "adosc",
        df_ta,
    )


def display_obv(df_stock: pd.DataFrame, s_ticker: str = "", export: str = ""):
    """Plot OBV technical indicator

    Parameters
    ----------
    df_stock : pd.DataFrame
        Dataframe of prices
    s_ticker : str
        Ticker
    export: str
        Format to export data as
    """
    bar_colors = ["r" if x[1].Open < x[1].Close else "g" for x in df_stock.iterrows()]

    bar_width = df_stock.index[1] - df_stock.index[0]

    divisor = 1_000_000
    df_vol = df_stock["Volume"].dropna()
    df_vol = df_vol.values / divisor
    df_ta = volume_model.obv(df_stock)
    df_cal = df_ta.values
    df_cal = df_cal / divisor

    fig, axes = plt.subplots(
        3,
        1,
        gridspec_kw={"height_ratios": [2, 1, 1]},
        figsize=plot_autoscale(),
        dpi=PLOT_DPI,
    )
    ax = axes[0]
    ax.plot(df_stock.index, df_stock["Adj Close"].values, "k", lw=2)
    ax.set_title(f"{s_ticker} OBV")
    ax.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax.set_ylabel("Price")
    ax.grid(b=True, which="major", color="#666666", linestyle="-")
    ax.minorticks_on()
    ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    ax2 = axes[1]
    ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax2.set_ylabel("Volume [M]")
    ax2.bar(
        df_stock.index,
        df_vol,
        color=bar_colors,
        alpha=0.8,
        width=bar_width,
    )
    ax3 = axes[2]
    ax3.set_ylabel("OBV [M]")
    ax3.set_xlabel("Time")
    ax3.plot(df_ta.index, df_cal, "b", lw=1)
    ax3.set_xlim(df_stock.index[0], df_stock.index[-1])
    ax3.grid(b=True, which="major", color="#666666", linestyle="-")
    ax3.minorticks_on()
    ax3.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

    if gtff.USE_ION:
        plt.ion()

    plt.gcf().autofmt_xdate()
    fig.tight_layout(pad=1)

    plt.show()
    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "obv",
        df_ta,
    )

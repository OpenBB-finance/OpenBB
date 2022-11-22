"""Momentum View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import mplfinance as mpf

from openbb_terminal.config_terminal import theme
from openbb_terminal.common.technical_analysis import momentum_model
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    reindex_dates,
    is_valid_axes_count,
    print_rich_table,
)
from openbb_terminal.rich_config import console
from openbb_terminal.common.technical_analysis import ta_helpers

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def display_cci(
    data: pd.DataFrame,
    window: int = 14,
    scalar: float = 0.0015,
    symbol: str = "",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots CCI Indicator

    Parameters
    ----------

    data : pd.DataFrame
        Dataframe of OHLC
    window : int
        Length of window
    scalar : float
        Scalar variable
    symbol : str
        Stock ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """

    df_ta = momentum_model.cci(data, window, scalar)
    plot_data = pd.merge(data, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    # This plot has 2 axes
    if external_axes is None:
        _, axes = plt.subplots(
            2, 1, figsize=plot_autoscale(), sharex=True, dpi=PLOT_DPI
        )
        (ax1, ax2) = axes
    elif is_valid_axes_count(external_axes, 2):
        (ax1, ax2) = external_axes
    else:
        return

    close_col = ta_helpers.check_columns(data)
    if close_col is None:
        return
    ax1.set_title(f"{symbol} CCI")
    ax1.plot(
        plot_data.index,
        plot_data[close_col].values,
    )
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel("Share Price ($)")

    theme.style_primary_axis(
        ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax2.plot(plot_data.index, plot_data[df_ta.columns[0]].values)
    ax2.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax2.axhspan(100, ax2.get_ylim()[1], facecolor=theme.down_color, alpha=0.2)
    ax2.axhspan(ax2.get_ylim()[0], -100, facecolor=theme.up_color, alpha=0.2)

    theme.style_primary_axis(
        ax2,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax3 = ax2.twinx()
    ax3.set_ylim(ax2.get_ylim())
    ax3.axhline(100, color=theme.down_color, ls="--")
    ax3.axhline(-100, color=theme.up_color, ls="--")

    theme.style_twin_axis(ax3)

    ax2.set_yticks([-100, 100])
    ax2.set_yticklabels(["OVERSOLD", "OVERBOUGHT"])

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "cci",
        df_ta,
    )


@log_start_end(log=logger)
def display_macd(
    data: pd.Series,
    n_fast: int = 12,
    n_slow: int = 26,
    n_signal: int = 9,
    symbol: str = "",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots MACD signal

    Parameters
    ----------
    data : pd.Series
        Values to input
    n_fast : int
        Fast period
    n_slow : int
        Slow period
    n_signal : int
        Signal period
    symbol : str
        Stock ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    df_ta = momentum_model.macd(data, n_fast, n_slow, n_signal)
    plot_data = pd.merge(data, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    # This plot has 2 axes
    if external_axes is None:
        _, axes = plt.subplots(
            2, 1, figsize=plot_autoscale(), sharex=True, dpi=PLOT_DPI
        )
        (ax1, ax2) = axes
    elif is_valid_axes_count(external_axes, 2):
        (ax1, ax2) = external_axes
    else:
        return

    ax1.set_title(f"{symbol} MACD")
    ax1.plot(plot_data.index, plot_data.iloc[:, 1].values)
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel("Share Price ($)")
    theme.style_primary_axis(
        ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax2.plot(plot_data.index, plot_data.iloc[:, 2].values)
    ax2.plot(
        plot_data.index,
        plot_data.iloc[:, 4].values,
        color=theme.down_color,
    )
    ax2.bar(
        plot_data.index,
        plot_data.iloc[:, 3].values,
        width=theme.volume_bar_width,
        color=theme.up_color,
    )
    ax2.legend(
        [
            f"MACD Line {plot_data.columns[2]}",
            f"Signal Line {plot_data.columns[4]}",
            f"Histogram {plot_data.columns[3]}",
        ],
        loc=2,
        prop={"size": 6},
    )
    ax2.set_xlim(plot_data.index[0], plot_data.index[-1])
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
        "macd",
        df_ta,
    )


@log_start_end(log=logger)
def display_rsi(
    data: pd.Series,
    window: int = 14,
    scalar: float = 100.0,
    drift: int = 1,
    symbol: str = "",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots RSI Indicator

    Parameters
    ----------
    data : pd.Series
        Values to input
    window : int
        Length of window
    scalar : float
        Scalar variable
    drift : int
        Drift variable
    symbol : str
        Stock ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    if isinstance(data, pd.DataFrame):
        console.print("[red]Please send a series and not a dataframe[/red]\n")
        return
    df_ta = momentum_model.rsi(data, window, scalar, drift)

    # This plot has 2 axes
    if external_axes is None:
        _, axes = plt.subplots(
            2, 1, figsize=plot_autoscale(), sharex=True, dpi=PLOT_DPI
        )
        (ax1, ax2) = axes
    elif is_valid_axes_count(external_axes, 2):
        (ax1, ax2) = external_axes
    else:
        return

    plot_data = pd.merge(data, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    ax1.plot(plot_data.index, plot_data.iloc[:, 1].values)
    ax1.set_title(f"{symbol} RSI{window}")
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel("Share Price ($)")
    theme.style_primary_axis(
        ax=ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax2.plot(plot_data.index, plot_data[df_ta.columns[0]].values)
    ax2.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax2.axhspan(0, 30, facecolor=theme.up_color, alpha=0.2)
    ax2.axhspan(70, 100, facecolor=theme.down_color, alpha=0.2)
    ax2.set_ylim([0, 100])

    theme.style_primary_axis(
        ax=ax2,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax3 = ax2.twinx()
    ax3.set_ylim(ax2.get_ylim())
    ax3.axhline(30, color=theme.up_color, ls="--")
    ax3.axhline(70, color=theme.down_color, ls="--")
    ax2.set_yticks([30, 70])
    ax2.set_yticklabels(["OVERSOLD", "OVERBOUGHT"])

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "rsi",
        df_ta,
    )


@log_start_end(log=logger)
def display_stoch(
    data: pd.DataFrame,
    fastkperiod: int = 14,
    slowdperiod: int = 3,
    slowkperiod: int = 3,
    symbol: str = "",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
) -> None:
    """Plots stochastic oscillator signal

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of OHLC prices
    fastkperiod : int
        Fast k period
    slowdperiod : int
        Slow d period
    slowkperiod : int
        Slow k period
    symbol : str
        Stock ticker symbol
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
    """
    close_col = ta_helpers.check_columns(data)
    if close_col is None:
        return
    df_ta = momentum_model.stoch(
        data,
        fastkperiod,
        slowdperiod,
        slowkperiod,
    )
    # This plot has 3 axes
    if not external_axes:
        _, axes = plt.subplots(
            2, 1, sharex=True, figsize=plot_autoscale(), dpi=PLOT_DPI
        )
        ax1, ax2 = axes
        ax3 = ax2.twinx()
    elif is_valid_axes_count(external_axes, 3):
        (ax1, ax2, ax3) = external_axes
    else:
        return

    plot_data = pd.merge(data, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    ax1.plot(plot_data.index, plot_data[close_col].values)

    ax1.set_title(f"Stochastic Relative Strength Index (STOCH RSI) on {symbol}")
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel("Share Price ($)")
    theme.style_primary_axis(
        ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax2.plot(plot_data.index, plot_data[df_ta.columns[0]].values)
    ax2.plot(plot_data.index, plot_data[df_ta.columns[1]].values, ls="--")
    ax2.set_xlim(plot_data.index[0], plot_data.index[-1])
    theme.style_primary_axis(
        ax2,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax3.set_ylim(ax2.get_ylim())
    ax3.axhspan(80, 100, facecolor=theme.down_color, alpha=0.2)
    ax3.axhspan(0, 20, facecolor=theme.up_color, alpha=0.2)
    ax3.axhline(80, color=theme.down_color, ls="--")
    ax3.axhline(20, color=theme.up_color, ls="--")
    theme.style_twin_axis(ax3)

    ax2.set_yticks([20, 80])
    ax2.set_yticklabels(["OVERSOLD", "OVERBOUGHT"])
    ax2.legend(
        [f"%K {df_ta.columns[0]}", f"%D {df_ta.columns[1]}"],
        loc=2,
        prop={"size": 6},
    )

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "stoch",
        df_ta,
    )


@log_start_end(log=logger)
def display_fisher(
    data: pd.DataFrame,
    window: int = 14,
    symbol: str = "",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots Fisher Indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of OHLC prices
    window : int
        Length of window
    symbol : str
        Ticker string
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
    """
    df_ta = momentum_model.fisher(data, window)
    if df_ta.empty:
        return
    plot_data = pd.merge(data, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    # This plot has 3 axes
    if not external_axes:
        _, axes = plt.subplots(
            2, 1, sharex=True, figsize=plot_autoscale(), dpi=PLOT_DPI
        )
        ax1, ax2 = axes
        ax3 = ax2.twinx()
    elif is_valid_axes_count(external_axes, 3):
        (ax1, ax2, ax3) = external_axes
    else:
        return

    ax1.set_title(f"{symbol} Fisher Transform")
    close_col = ta_helpers.check_columns(data)
    if close_col is None:
        return
    ax1.plot(plot_data.index, plot_data[close_col].values)
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel("Price")
    theme.style_primary_axis(
        ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax2.plot(
        plot_data.index,
        plot_data[df_ta.columns[0]].values,
        label="Fisher",
    )
    ax2.plot(
        plot_data.index,
        plot_data[df_ta.columns[1]].values,
        label="Signal",
    )
    ax2.set_xlim(plot_data.index[0], plot_data.index[-1])
    theme.style_primary_axis(
        ax2,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax3.set_ylim(ax2.get_ylim())
    ax3.axhspan(2, ax2.get_ylim()[1], facecolor=theme.down_color, alpha=0.2)
    ax3.axhspan(ax2.get_ylim()[0], -2, facecolor=theme.up_color, alpha=0.2)
    ax3.axhline(2, color=theme.down_color, ls="--")
    ax3.axhline(-2, color=theme.up_color, ls="--")
    theme.style_twin_axis(ax3)

    ax2.set_yticks([-2, 0, 2])
    ax2.set_yticklabels(["-2 STDEV", "0", "+2 STDEV"])
    ax2.legend(loc=2, prop={"size": 6})

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "fisher",
        df_ta,
    )


@log_start_end(log=logger)
def display_cg(
    data: pd.Series,
    window: int = 14,
    symbol: str = "",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots center of gravity Indicator

    Parameters
    ----------
    data : pd.Series
        Series of values
    window : int
        Length of window
    symbol : str
        Stock ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    df_ta = momentum_model.cg(data, window)
    plot_data = pd.merge(data, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    # This plot has 2 axes
    if external_axes is None:
        _, axes = plt.subplots(
            2, 1, figsize=plot_autoscale(), sharex=True, dpi=PLOT_DPI
        )
        (ax1, ax2) = axes
    elif is_valid_axes_count(external_axes, 2):
        (ax1, ax2) = external_axes
    else:
        return

    ax1.set_title(f"{symbol} Centre of Gravity")
    ax1.plot(plot_data.index, plot_data[data.name].values)
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel("Share Price ($)")
    theme.style_primary_axis(
        ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax2.plot(plot_data.index, plot_data[df_ta.columns[0]].values, label="CG")
    # shift cg 1 bar forward for signal
    signal = np.roll(plot_data[df_ta.columns[0]].values, 1)
    ax2.plot(plot_data.index, signal, label="Signal")
    ax2.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax2.legend()
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
        "cg",
        df_ta,
    )


@log_start_end(log=logger)
def display_clenow_momentum(
    data: pd.Series,
    symbol: str = "",
    window: int = 90,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Prints table and plots clenow momentum

    Parameters
    ----------
    data : pd.Series
        Series of values
    symbol : str
        Symbol that the data corresponds to
    window : int
        Length of window
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> df = openbb.stocks.load("AAPL")
    >>> openbb.ta.clenow_chart(df["Close"])
    """
    r2, coef, fit_data = momentum_model.clenow_momentum(data, window)

    df = pd.DataFrame.from_dict(
        {
            "R^2": f"{r2:.5f}",
            "Fit Coef": f"{coef:.5f}",
            "Factor": f"{coef * r2:.5f}",
        },
        orient="index",
    )
    print_rich_table(
        df,
        show_index=True,
        headers=[""],
        title=f"Clenow Exponential Regression Factor on {symbol}",
        show_header=False,
    )

    # This plot has 2 axes
    if external_axes is None:
        _, ax1 = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    elif is_valid_axes_count(external_axes, 1):
        ax1 = external_axes
    else:
        return

    ax1.plot(data.index, np.log(data.values))
    ax1.plot(data.index[-window:], fit_data, linewidth=2)

    ax1.set_title(f"Clenow Momentum Exponential Regression on {symbol}")
    ax1.set_xlim(data.index[0], data.index[-1])
    ax1.set_ylabel("Log Price")
    theme.style_primary_axis(
        ax1,
    )
    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "clenow",
    )


def display_demark(
    data: pd.DataFrame,
    symbol: str = "",
    min_to_show: int = 5,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plot demark sequential indicator

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame of values
    symbol : str
        Symbol that the data corresponds to
    min_to_show: int
        Minimum value to show
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axes are expected in the list), by default None

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> df = openbb.stocks.load("AAPL")
    >>> openbb.ta.demark_chart(df)
    """
    close_col = ta_helpers.check_columns(data, high=False, low=False)
    if close_col is None:
        return
    demark_df = momentum_model.demark_seq(data[close_col])
    demark_df.index = data.index

    stock_data = data.copy()
    stock_data["up"] = demark_df.TD_SEQ_UPa
    stock_data["down"] = demark_df.TD_SEQ_DNa

    # MPLfinance can do series of markers :)
    markersUP = (
        stock_data["up"]
        .apply(lambda x: f"${x}$" if x > min_to_show else None)
        .to_list()
    )
    markersDOWN = (
        stock_data["down"]
        .apply(lambda x: f"${x}$" if x > min_to_show else None)
        .to_list()
    )

    adp = [
        mpf.make_addplot(
            0.98 * stock_data["Low"],
            type="scatter",
            markersize=30,
            marker=markersDOWN,
            color="r",
        ),
        mpf.make_addplot(
            1.012 * stock_data["High"],
            type="scatter",
            markersize=30,
            marker=markersUP,
            color="b",
        ),
    ]

    # Stuff for mplfinance
    candle_chart_kwargs = {
        "type": "ohlc",
        "style": theme.mpf_style,
        "volume": False,
        "addplot": adp,
        "xrotation": theme.xticks_rotation,
        "scale_padding": {"left": 0.3, "right": 1, "top": 0.8, "bottom": 0.8},
        "update_width_config": {
            "candle_linewidth": 0.6,
            "candle_width": 0.8,
            "volume_linewidth": 0.8,
            "volume_width": 0.8,
        },
        "warn_too_much_data": 10000,
    }
    if external_axes is None:
        candle_chart_kwargs["returnfig"] = True
        candle_chart_kwargs["figratio"] = (10, 7)
        candle_chart_kwargs["figscale"] = 1.10
        candle_chart_kwargs["figsize"] = plot_autoscale()
        candle_chart_kwargs["warn_too_much_data"] = 100_000

        fig, _ = mpf.plot(stock_data, **candle_chart_kwargs)
        fig.suptitle(
            f"{symbol} Demark Sequential",
            x=0.055,
            y=0.965,
            horizontalalignment="left",
        )
        theme.visualize_output(force_tight_layout=False)

    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of 1 axis items.\n[/red]")
        ax1 = external_axes
        candle_chart_kwargs["ax"] = ax1
        mpf.plot(stock_data, **candle_chart_kwargs)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "demark",
        stock_data,
    )

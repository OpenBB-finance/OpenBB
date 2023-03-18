"""Volatility Technical Indicators View"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd

from openbb_terminal.common.technical_analysis import ta_helpers, volatility_model
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
    reindex_dates,
)

logger = logging.getLogger(__name__)

# pylint: disable=too-many-arguments


@log_start_end(log=logger)
def display_bbands(
    data: pd.DataFrame,
    symbol: str = "",
    window: int = 15,
    n_std: float = 2,
    mamode: str = "sma",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots bollinger bands

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    symbol : str
        Ticker symbol
    window : int
        Length of window to calculate BB
    n_std : float
        Number of standard deviations to show
    mamode : str
        Method of calculating average
    export : str
        Format of export file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_ta = volatility_model.bbands(data, window, n_std, mamode)
    plot_data = pd.merge(data, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    close_col = ta_helpers.check_columns(data, high=False, low=False)
    if close_col is None:
        return
    ax.plot(
        plot_data.index,
        plot_data[close_col].values,
    )
    ax.plot(
        plot_data.index,
        plot_data[df_ta.columns[0]].values,
        theme.down_color,
        linewidth=0.7,
    )
    ax.plot(plot_data.index, plot_data[df_ta.columns[1]].values, ls="--", linewidth=0.7)
    ax.plot(
        plot_data.index,
        plot_data[df_ta.columns[2]].values,
        theme.up_color,
        linewidth=0.7,
    )
    ax.set_title(f"{symbol} Bollinger Bands")
    ax.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax.set_ylabel("Share Price ($)")
    ax.legend([symbol, df_ta.columns[0], df_ta.columns[1], df_ta.columns[2]])
    ax.fill_between(
        df_ta.index, df_ta.iloc[:, 0].values, df_ta.iloc[:, 2].values, alpha=0.1
    )
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
        "bbands",
        df_ta,
        sheet_name,
    )


@log_start_end(log=logger)
def display_donchian(
    data: pd.DataFrame,
    symbol: str = "",
    upper_length: int = 20,
    lower_length: int = 20,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots donchian channels

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    symbol : str
        Ticker symbol
    upper_length : int
        Length of window to calculate upper channel
    lower_length : int
        Length of window to calculate lower channel
    export : str
        Format of export file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_ta = volatility_model.donchian(data, upper_length, lower_length)
    plot_data = pd.merge(data, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    close_col = ta_helpers.check_columns(data)
    if close_col is None:
        return
    ax.plot(plot_data.index, plot_data[close_col].values)
    ax.plot(
        plot_data.index,
        plot_data[df_ta.columns[0]].values,
        linewidth=0.7,
        label="Upper",
    )
    ax.plot(plot_data.index, plot_data[df_ta.columns[1]].values, linewidth=0.7, ls="--")
    ax.plot(
        plot_data.index,
        plot_data[df_ta.columns[2]].values,
        linewidth=0.7,
        label="Lower",
    )
    ax.fill_between(
        plot_data.index,
        plot_data[df_ta.columns[0]].values,
        plot_data[df_ta.columns[2]].values,
        alpha=0.1,
    )
    ax.set_title(f"{symbol} donchian")
    ax.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax.set_ylabel("Price ($)")
    ax.legend([symbol, df_ta.columns[0], df_ta.columns[1], df_ta.columns[2]])
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
        "donchian",
        df_ta,
        sheet_name,
    )


@log_start_end(log=logger)
def view_kc(
    data: pd.DataFrame,
    window: int = 20,
    scalar: float = 2,
    mamode: str = "ema",
    offset: int = 0,
    symbol: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots Keltner Channels Indicator

    Parameters
    ----------

    data: pd.DataFrame
        Dataframe of ohlc prices
    window: int
        Length of window
    scalar: float
        Scalar value
    mamode: str
        Type of filter
    offset: int
        Offset value
    symbol: str
        Ticker symbol
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data
    external_axes: Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    df_ta = volatility_model.kc(
        data,
        window,
        scalar,
        mamode,
        offset,
    )
    plot_data = pd.merge(data, df_ta, how="outer", left_index=True, right_index=True)
    plot_data = reindex_dates(plot_data)

    # This plot has 1 axis
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    close_col = ta_helpers.check_columns(data)
    if close_col is None:
        return
    ax.plot(plot_data.index, plot_data[close_col].values)
    ax.plot(
        plot_data.index,
        plot_data[df_ta.columns[0]].values,
        linewidth=0.7,
        label="Upper",
    )
    ax.plot(plot_data.index, plot_data[df_ta.columns[1]].values, linewidth=0.7, ls="--")
    ax.plot(
        plot_data.index,
        plot_data[df_ta.columns[2]].values,
        linewidth=0.7,
        label="Lower",
    )
    ax.fill_between(
        plot_data.index,
        plot_data[df_ta.columns[0]].values,
        plot_data[df_ta.columns[2]].values,
        alpha=0.1,
    )
    ax.set_title(f"{symbol} Keltner Channels")
    ax.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax.set_ylabel("Price")
    ax.legend([symbol, df_ta.columns[0], df_ta.columns[1], df_ta.columns[2]])
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
        "kc",
        df_ta,
        sheet_name,
    )


@log_start_end(log=logger)
def display_atr(
    data: pd.DataFrame,
    symbol: str = "",
    window: int = 14,
    mamode: str = "sma",
    offset: int = 0,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots ATR

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    symbol : str
        Ticker symbol
    window : int
        Length of window to calculate upper channel
    export : str
        Format of export file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    df_ta = volatility_model.atr(data, window=window, mamode=mamode, offset=offset)

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

    ax1.plot(plot_data.index, plot_data.iloc[:, 1].values, color=theme.get_colors()[0])
    ax1.set_title(f"{symbol} ATR")
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel("Share Price ($)")
    theme.style_primary_axis(
        ax=ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax2.plot(
        plot_data.index, plot_data[df_ta.columns[0]].values, color=theme.get_colors()[1]
    )
    ax2.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax2.set_ylabel("ATR")
    theme.style_primary_axis(
        ax=ax2,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )
    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
        "atr",
        df_ta,
        sheet_name,
    )


@log_start_end(log=logger)
def display_cones(
    data: pd.DataFrame,
    symbol: str = "",
    lower_q: float = 0.25,
    upper_q: float = 0.75,
    model: str = "STD",
    is_crypto: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Plots the realized volatility quantiles for the loaded ticker.
    The model used to calculate the volatility is selectable.

    Parameters
    ----------
    data: pd.DataFrame
        DataFrame of OHLC prices.
    symbol: str (default = "")
        The ticker symbol.
    lower_q: float (default = 0.25)
        The lower quantile to calculate for.
    upper_q: float (default = 0.75)
        The upper quantile to for.
    is_crypto: bool (default = False)
        If true, volatility is calculated for 365 days instead of 252.
    model: str (default = "STD")
        The model to use for volatility calculation. Choices are:
        ["STD", "Parkinson", "Garman-Klass", "Hodges-Tompkins", "Rogers-Satchell", "Yang-Zhang"]

            Standard deviation measures how widely returns are dispersed from the average return.
            It is the most common (and biased) estimator of volatility.

            Parkinson volatility uses the high and low price of the day rather than just close to close prices.
            It is useful for capturing large price movements during the day.

            Garman-Klass volatility extends Parkinson volatility by taking into account the opening and closing price.
            As markets are most active during the opening and closing of a trading session;
            it makes volatility estimation more accurate.

            Hodges-Tompkins volatility is a bias correction for estimation using an overlapping data sample.
            It produces unbiased estimates and a substantial gain in efficiency.

            Rogers-Satchell is an estimator for measuring the volatility with an average return not equal to zero.
            Unlike Parkinson and Garman-Klass estimators, Rogers-Satchell incorporates a drift term,
            mean return not equal to zero.

            Yang-Zhang volatility is the combination of the overnight (close-to-open volatility).
            It is a weighted average of the Rogers-Satchell volatility and the open-to-close volatility.
    export : str
        Format of export file
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.

    Examples
    --------
    df_ta = openbb.stocks.load('XLY')
    openbb.ta.cones_chart(data = df_ta, symbol = 'XLY')

    df_ta = openbb.stocks.load('XLE')
    openbb.ta.cones_chart(data = df_ta, symbol = "XLE", lower_q = 0.10, upper_q = 0.90)

    openbb.ta.cones_chart(data = df_ta, symbol = "XLE", model = "Garman-Klass")
    """

    if lower_q > upper_q:
        lower_q, upper_q = upper_q, lower_q

    df_ta = volatility_model.cones(
        data, lower_q=lower_q, upper_q=upper_q, is_crypto=is_crypto, model=model
    )
    lower_q_label = str(int(lower_q * 100))
    upper_q_label = str(int(upper_q * 100))
    if not df_ta.empty:
        plt.figure(figsize=[14, 7])
        plt.autoscale(enable=True, axis="both", tight=True)
        plt.plot(df_ta.index, df_ta.Min, "-o", linewidth=1, label="Min")
        plt.plot(df_ta.index, df_ta.Max, "-o", linewidth=1, label="Max")
        plt.plot(df_ta.index, df_ta.Median, "-o", linewidth=1, label="Median")
        plt.plot(
            df_ta.index,
            df_ta["Upper " f"{upper_q_label}" "%"],
            "-o",
            linewidth=1,
            label="Upper " f"{upper_q_label}" "%",
        )
        plt.plot(
            df_ta.index,
            df_ta["Lower " f"{lower_q_label}" "%"],
            "-o",
            linewidth=1,
            label="Lower " f"{lower_q_label}" "%",
        )
        plt.plot(df_ta.index, df_ta.Realized, "o-.", linewidth=1, label="Realized")
        plt.xlabel(xlabel="Window of Time (in days)", labelpad=20, y=0)
        plt.title(
            label=f"{symbol}" " - Realized Volatility Cones - " f"{model}" " Model",
            loc="center",
            y=1.0,
        )
        plt.legend(loc="best", ncol=6, fontsize="x-small")
        plt.tick_params(axis="y", which="both", labelleft=False, labelright=True)
        plt.xticks(df_ta.index)
        plt.tight_layout(pad=2.0)

        theme.visualize_output()

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks"),
            "cones",
            df_ta,
            sheet_name,
        )

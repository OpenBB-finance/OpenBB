"""Volume View"""
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.pyplot as plt
import pandas as pd

from openbb_terminal.common.technical_analysis import ta_helpers, volume_model
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
    reindex_dates,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_ad(
    data: pd.DataFrame,
    use_open: bool = False,
    symbol: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots AD technical indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    use_open : bool
        Whether to use open prices in calculation
    symbol : str
        Ticker symbol
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data as
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
    """
    divisor = 1_000_000
    df_vol = data["Volume"] / divisor
    df_vol.name = "Adj Volume"
    df_ta = volume_model.ad(data, use_open)
    # check if AD exists in dataframe
    if "AD" in df_ta.columns:
        df_cal = df_ta["AD"] / divisor
    elif "ADo" in df_ta.columns:
        df_cal = df_ta["ADo"] / divisor
    else:
        console.print("AD not found in dataframe")
        return
    df_cal.name = "Adj AD"

    plot_data = pd.merge(data, df_vol, how="outer", left_index=True, right_index=True)
    plot_data = pd.merge(
        plot_data, df_ta, how="outer", left_index=True, right_index=True
    )
    plot_data = pd.merge(
        plot_data, df_cal, how="outer", left_index=True, right_index=True
    )
    plot_data = reindex_dates(plot_data)

    # This plot has 3 axes
    if external_axes is None:
        _, axes = plt.subplots(
            3,
            1,
            sharex=True,
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
        ax1, ax2, ax3 = axes
    elif is_valid_axes_count(external_axes, 3):
        (ax1, ax2, ax3) = external_axes
    else:
        return

    close_col = ta_helpers.check_columns(data)
    if close_col is None:
        return
    ax1.plot(plot_data.index, plot_data[close_col].values)
    ax1.set_title(f"{symbol} AD", x=0.04, y=1)
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel("Price")
    theme.style_primary_axis(
        ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax2.set_ylabel("Volume [M]")
    bar_colors = [
        theme.down_color if x[1].Open < x[1].Close else theme.up_color
        for x in plot_data.iterrows()
    ]
    ax2.bar(
        plot_data.index,
        plot_data["Adj Volume"].values,
        color=bar_colors,
        width=theme.volume_bar_width,
    )
    ax2.set_xlim(plot_data.index[0], plot_data.index[-1])
    theme.style_primary_axis(
        ax2,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax3.set_ylabel("A/D [M]")
    ax3.plot(plot_data.index, plot_data["Adj AD"])
    ax3.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax3.axhline(0, linestyle="--")
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
        "ad",
        df_ta,
        sheet_name,
    )


@log_start_end(log=logger)
def display_adosc(
    data: pd.DataFrame,
    fast: int = 3,
    slow: int = 10,
    use_open: bool = False,
    symbol: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots AD Osc Indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    use_open : bool
        Whether to use open prices in calculation
    fast: int
        Length of fast window
    slow : int
        Length of slow window
    symbol : str
        Stock ticker
    export : str
        Format to export data
    external_axes : Optional[List[plt.Axes]], optional
        External axes (3 axes are expected in the list), by default None
    """
    divisor = 1_000_000
    df_vol = data["Volume"] / divisor
    df_vol.name = "Adj Volume"
    df_ta = volume_model.adosc(data, use_open, fast, slow)
    df_cal = df_ta[df_ta.columns[0]] / divisor
    df_cal.name = "Adj ADOSC"

    plot_data = pd.merge(data, df_vol, how="outer", left_index=True, right_index=True)
    plot_data = pd.merge(
        plot_data, df_ta, how="outer", left_index=True, right_index=True
    )
    plot_data = pd.merge(
        plot_data, df_cal, how="outer", left_index=True, right_index=True
    )
    plot_data = reindex_dates(plot_data)

    # This plot has 3 axes
    if external_axes is None:
        _, axes = plt.subplots(
            3,
            1,
            sharex=True,
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
        ax1, ax2, ax3 = axes
    elif is_valid_axes_count(external_axes, 3):
        (ax1, ax2, ax3) = external_axes
    else:
        return

    ax1.set_title(f"{symbol} AD Oscillator")
    ax1.plot(plot_data.index, plot_data["Adj Close"].values)
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel("Price")
    theme.style_primary_axis(
        ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax2.set_ylabel("Volume [M]")
    bar_colors = [
        theme.down_color if x[1].Open < x[1].Close else theme.up_color
        for x in plot_data.iterrows()
    ]
    ax2.bar(
        plot_data.index,
        plot_data["Adj Volume"],
        color=bar_colors,
        width=theme.volume_bar_width,
    )
    ax2.set_xlim(plot_data.index[0], plot_data.index[-1])
    theme.style_primary_axis(
        ax2,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax3.set_ylabel("AD Osc [M]")
    ax3.plot(plot_data.index, plot_data["Adj ADOSC"], label="AD Osc")
    ax3.set_xlim(plot_data.index[0], plot_data.index[-1])
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
        "adosc",
        df_ta,
        sheet_name,
    )


@log_start_end(log=logger)
def display_obv(
    data: pd.DataFrame,
    symbol: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots OBV technical indicator

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of ohlc prices
    symbol : str
        Ticker
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Format to export data as
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    divisor = 1_000_000
    df_vol = data["Volume"] / divisor
    df_vol.name = "Adj Volume"
    df_ta = volume_model.obv(data)
    df_cal = df_ta[df_ta.columns[0]] / divisor
    df_cal.name = "Adj OBV"

    plot_data = pd.merge(data, df_vol, how="outer", left_index=True, right_index=True)
    plot_data = pd.merge(
        plot_data, df_ta, how="outer", left_index=True, right_index=True
    )
    plot_data = pd.merge(
        plot_data, df_cal, how="outer", left_index=True, right_index=True
    )
    plot_data = reindex_dates(plot_data)

    # This plot has 3 axes
    if external_axes is None:
        _, axes = plt.subplots(
            3,
            1,
            sharex=True,
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
        ax1, ax2, ax3 = axes
    elif is_valid_axes_count(external_axes, 3):
        (ax1, ax2, ax3) = external_axes
    else:
        return

    close_col = ta_helpers.check_columns(data)
    if close_col is None:
        return
    ax1.plot(plot_data.index, plot_data[close_col].values)
    ax1.set_title(f"{symbol} OBV")
    ax1.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax1.set_ylabel("Price")
    theme.style_primary_axis(
        ax1,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax2.set_xlim(plot_data.index[0], plot_data.index[-1])
    ax2.set_ylabel("Volume [M]")
    bar_colors = [
        theme.down_color if x[1].Open < x[1].Close else theme.up_color
        for x in plot_data.iterrows()
    ]
    ax2.bar(
        plot_data.index,
        plot_data["Adj Volume"],
        color=bar_colors,
        alpha=0.8,
        width=theme.volume_bar_width,
    )
    theme.style_primary_axis(
        ax2,
        data_index=plot_data.index.to_list(),
        tick_labels=plot_data["date"].to_list(),
    )

    ax3.set_ylabel("OBV [M]")
    ax3.plot(plot_data.index, plot_data["Adj OBV"])
    ax3.set_xlim(plot_data.index[0], plot_data.index[-1])
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
        "obv",
        df_ta,
        sheet_name,
    )

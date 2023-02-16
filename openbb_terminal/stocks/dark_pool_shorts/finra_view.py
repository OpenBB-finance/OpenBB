""" FINRA View """
__docformat__ = "numpy"

import logging
import os
from typing import List, Optional

import matplotlib.dates as mdates
import pandas as pd
from matplotlib import pyplot as plt

from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    is_valid_axes_count,
    plot_autoscale,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.dark_pool_shorts import finra_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def darkpool_ats_otc(
    symbol: str,
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display barchart of dark pool (ATS) and OTC (Non ATS) data. [Source: FINRA]

    Parameters
    ----------
    symbol : str
        Stock ticker
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (2 axes are expected in the list), by default None
    """
    ats, otc = finra_model.getTickerFINRAdata(symbol)
    if ats.empty:
        console.print("[red]Could not get data[/red]\n")
        return

    if ats.empty and otc.empty:
        console.print("No ticker data found!")

    # This plot has 2 axes
    if not external_axes:
        _, axes = plt.subplots(
            2, 1, sharex=True, figsize=plot_autoscale(), dpi=PLOT_DPI
        )
        (ax1, ax2) = axes
    elif is_valid_axes_count(external_axes, 2):
        (ax1, ax2) = external_axes
    else:
        return

    if not ats.empty and not otc.empty:
        ax1.bar(
            ats.index,
            (ats["totalWeeklyShareQuantity"] + otc["totalWeeklyShareQuantity"])
            / 1_000_000,
            color=theme.down_color,
        )
        ax1.bar(
            otc.index, otc["totalWeeklyShareQuantity"] / 1_000_000, color=theme.up_color
        )
        ax1.legend(["ATS", "OTC"])

    elif not ats.empty:
        ax1.bar(
            ats.index,
            ats["totalWeeklyShareQuantity"] / 1_000_000,
            color=theme.down_color,
        )
        ax1.legend(["ATS"])

    elif not otc.empty:
        ax1.bar(
            otc.index, otc["totalWeeklyShareQuantity"] / 1_000_000, color=theme.up_color
        )
        ax1.legend(["OTC"])

    ax1.set_ylabel("Total Weekly Shares [Million]")
    ax1.set_title(f"Dark Pools (ATS) vs OTC (Non-ATS) Data for {symbol}")
    ax1.set_xticks([])

    if not ats.empty:
        ax2.plot(
            ats.index,
            ats["totalWeeklyShareQuantity"] / ats["totalWeeklyTradeCount"],
            color=theme.down_color,
        )
        ax2.legend(["ATS"])

        if not otc.empty:
            ax2.plot(
                otc.index,
                otc["totalWeeklyShareQuantity"] / otc["totalWeeklyTradeCount"],
                color=theme.up_color,
            )
            ax2.legend(["ATS", "OTC"])

    else:
        ax2.plot(
            otc.index,
            otc["totalWeeklyShareQuantity"] / otc["totalWeeklyTradeCount"],
            color=theme.up_color,
        )
        ax2.legend(["OTC"])

    ax2.set_ylabel("Shares per Trade")
    ax2.xaxis.set_major_locator(mdates.DayLocator(interval=10))
    ax2.set_xlim(otc.index[0], otc.index[-1])
    ax2.set_xlabel("Weeks")

    theme.style_primary_axis(ax1)
    theme.style_primary_axis(ax2)

    if not external_axes:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dpotc_ats",
        ats,
        sheet_name,
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dpotc_otc",
        otc,
        sheet_name,
    )


@log_start_end(log=logger)
def plot_dark_pools_ats(
    data: pd.DataFrame,
    symbols: List,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Plots promising tickers based on growing ATS data

    Parameters
    ----------
    data: pd.DataFrame
        Dark Pools (ATS) Data
    symbols: List
        List of tickers from most promising with better linear regression slope
    external_axes: Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None

    """

    # This plot has 1 axis
    if not external_axes:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    elif is_valid_axes_count(external_axes, 1):
        (ax,) = external_axes
    else:
        return

    for symbol in symbols:
        ax.plot(
            pd.to_datetime(
                data[data["issueSymbolIdentifier"] == symbol]["weekStartDate"]
            ),
            data[data["issueSymbolIdentifier"] == symbol]["totalWeeklyShareQuantity"]
            / 1_000_000,
        )

    ax.legend(symbols)
    ax.set_ylabel("Total Weekly Shares [Million]")
    ax.set_title("Dark Pool (ATS) growing tickers")
    ax.set_xlabel("Weeks")
    data["weekStartDate"] = pd.to_datetime(data["weekStartDate"])
    ax.set_xlim(data["weekStartDate"].iloc[0], data["weekStartDate"].iloc[-1])
    theme.style_primary_axis(ax)

    if not external_axes:
        theme.visualize_output()


@log_start_end(log=logger)
def darkpool_otc(
    input_limit: int = 1000,
    limit: int = 10,
    tier: str = "T1",
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display dark pool (ATS) data of tickers with growing trades activity. [Source: FINRA]

    Parameters
    ----------
    input_limit : int
        Number of tickers to filter from entire ATS data based on
        the sum of the total weekly shares quantity
    limit : int
        Number of tickers to display from most promising with
        better linear regression slope
    tier : str
        Tier to process data from: T1, T2 or OTCE
    export : str
        Export dataframe data to csv,json,xlsx file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    # TODO: Improve command logic to be faster and more useful
    df_ats, d_ats_reg = finra_model.getATSdata(input_limit, tier)

    if not df_ats.empty and d_ats_reg:
        symbols = list(
            dict(
                sorted(d_ats_reg.items(), key=lambda item: item[1], reverse=True)
            ).keys()
        )[:limit]

        plot_dark_pools_ats(df_ats, symbols, external_axes)

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "prom",
            df_ats,
            sheet_name,
        )
    else:
        console.print("[red]Could not get data[/red]\n")
        return
